/**
 * Gmail sales watcher: Google Apps Script.
 *
 * Depop, Poshmark, Vinted, Whatnot, and Mercari have no public API, but each emails you when an item sells.
 * This script runs every 10 minutes, finds new sale emails, pulls the item title and price,
 * appends a row to a "sales_inbox" tab in a Google Sheet, and emails you a DELIST reminder
 * that names the other platforms the item is listed on (if it finds the item in your inventory tab).
 *
 * Setup (about 10 minutes, see docs/07-automation.md):
 *  1. Create a Google Sheet. Import inventory/inventory.csv into a tab named "inventory".
 *     (Or keep the CSV as master and paste it into this tab weekly; the script only READS it.)
 *  2. Extensions > Apps Script. Paste this file. Set SHEET_ID below.
 *  3. Run setup() once, approve permissions. It creates the "sales_inbox" tab and a 10-minute trigger.
 *
 * Matching: the script looks for a SKU like CR-0042 in the email body first (put the SKU at the end of
 * every listing description). If none, it fuzzy-matches the email's item title against the inventory
 * "item" and "brand" columns. Unmatched sales still land in sales_inbox so nothing is lost.
 */

var SHEET_ID = 'PASTE_YOUR_GOOGLE_SHEET_ID_HERE';
var NOTIFY_EMAIL = Session.getActiveUser().getEmail();
var LABEL_DONE = 'resale/processed';

// Sender and subject patterns for sale notifications. Adjust if a platform changes wording.
var SOURCES = [
  { platform: 'depop',    query: 'from:(depop.com) subject:("You made a sale" OR "sold" OR "You\'ve sold")' },
  { platform: 'poshmark', query: 'from:(poshmark.com) subject:("Sold" OR "You made a sale" OR "Your item sold")' },
  { platform: 'vinted',   query: 'from:(vinted.com) subject:("sold" OR "You sold" OR "Your item has been sold" OR "Congratulations")' },
  { platform: 'whatnot',  query: 'from:(whatnot.com) subject:("sold" OR "Order" OR "You sold")' },
  { platform: 'mercari',  query: 'from:(mercari.com) subject:("sold" OR "Your item sold")' },
  { platform: 'ebay',     query: 'from:(ebay.com) subject:("Your item sold" OR "You made a sale")' },
  { platform: 'grailed',  query: 'from:(grailed.com) subject:("sold" OR "You made a sale")' },
];

function setup() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  if (!ss.getSheetByName('sales_inbox')) {
    var sh = ss.insertSheet('sales_inbox');
    sh.appendRow(['detected_at', 'platform', 'email_date', 'sku_guess', 'item_title', 'price', 'delist_from', 'subject', 'status']);
  }
  if (!GmailApp.getUserLabelByName(LABEL_DONE)) GmailApp.createLabel(LABEL_DONE);
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('checkSales').timeBased().everyMinutes(10).create();
  Logger.log('Setup done. checkSales runs every 10 minutes.');
}

function checkSales() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var inbox = ss.getSheetByName('sales_inbox');
  var inventory = loadInventory_(ss);
  var label = GmailApp.getUserLabelByName(LABEL_DONE);
  var found = [];

  SOURCES.forEach(function (src) {
    var threads = GmailApp.search(src.query + ' -label:' + LABEL_DONE + ' newer_than:7d', 0, 20);
    threads.forEach(function (thread) {
      thread.getMessages().forEach(function (msg) {
        var body = msg.getPlainBody() || '';
        var subject = msg.getSubject() || '';
        var text = subject + '\n' + body;
        var sku = (text.match(/\bCR-\d{4}\b/i) || [null])[0];
        var price = (text.match(/\$\s?(\d{1,4}(?:\.\d{2})?)/) || [null, ''])[1];
        var title = guessTitle_(subject, body);
        var match = sku ? inventory.bySku[sku.toUpperCase()] : fuzzyMatch_(title, inventory.rows);
        var delist = '';
        if (match) {
          sku = match.sku;
          delist = (match.listed_on || '').split('|').filter(function (p) { return p && p !== src.platform; }).join(', ');
        }
        inbox.appendRow([new Date(), src.platform, msg.getDate(), sku || '', title, price, delist, subject, match ? 'matched' : 'UNMATCHED']);
        found.push({ platform: src.platform, sku: sku, title: title, price: price, delist: delist, matched: !!match });
      });
      thread.addLabel(label);
    });
  });

  if (found.length) notify_(found);
}

function loadInventory_(ss) {
  var sh = ss.getSheetByName('inventory');
  var out = { rows: [], bySku: {} };
  if (!sh) return out;
  var data = sh.getDataRange().getValues();
  var head = data[0].map(String);
  for (var i = 1; i < data.length; i++) {
    var r = {};
    head.forEach(function (h, j) { r[h] = String(data[i][j] || ''); });
    if (r.sku && r.status !== 'sold') { out.rows.push(r); out.bySku[r.sku.toUpperCase()] = r; }
  }
  return out;
}

function guessTitle_(subject, body) {
  // Most platforms put the item name in quotes or after "sold" in the subject.
  var m = subject.match(/["“]([^"”]{4,80})["”]/) || body.match(/["“]([^"”]{4,80})["”]/);
  if (m) return m[1].trim();
  m = subject.match(/(?:sold|sale)[:!]?\s+(.{4,80})$/i);
  return m ? m[1].trim() : subject.slice(0, 80);
}

function fuzzyMatch_(title, rows) {
  if (!title) return null;
  var words = title.toLowerCase().split(/[^a-z0-9]+/).filter(function (w) { return w.length > 2; });
  var best = null, bestScore = 0;
  rows.forEach(function (r) {
    var hay = (r.brand + ' ' + r.item + ' ' + r.size).toLowerCase();
    var score = words.filter(function (w) { return hay.indexOf(w) >= 0; }).length;
    if (score > bestScore) { bestScore = score; best = r; }
  });
  return bestScore >= 2 ? best : null;
}

function notify_(found) {
  var lines = found.map(function (f) {
    var s = '[' + f.platform.toUpperCase() + '] ' + (f.sku || '(no SKU)') + '  ' + f.title + '  $' + f.price;
    if (f.delist) s += '\n   >>> DELIST NOW from: ' + f.delist.toUpperCase();
    if (!f.matched) s += '\n   (not matched to inventory, check sales_inbox)';
    return s;
  });
  GmailApp.sendEmail(NOTIFY_EMAIL, 'SALE: ' + found.length + ' new sale(s) - delist reminders inside', lines.join('\n\n'));
}
