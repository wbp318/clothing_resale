-- Seeded from docs/06-pricing-and-grading.md. Add a row every time you log a new tag.
CREATE TABLE IF NOT EXISTS tags (keyword TEXT, maker TEXT, era TEXT, band_low REAL, band_high REAL, note TEXT);
CREATE TABLE IF NOT EXISTS api_keys (key TEXT PRIMARY KEY, calls_left INTEGER, email TEXT);
INSERT INTO tags VALUES
 ('starter', 'Starter', '1985-1999', 40, 150, 'Satin and pullover jackets strongest'),
 ('nutmeg mills', 'Nutmeg Mills', '1988-1996', 30, 80, 'Pro and college tees and sweatshirts'),
 ('salem sportswear', 'Salem Sportswear', '1988-1995', 30, 90, 'Caricature player tees go higher'),
 ('logo 7', 'Logo 7', '1985-1998', 25, 70, ''),
 ('logo athletic', 'Logo Athletic', '1990-1999', 30, 90, 'Sharktooth jackets go higher'),
 ('chalk line', 'Chalk Line', '1988-1996', 40, 120, 'Fanimation jackets'),
 ('apex one', 'Apex One', '1990-1996', 40, 120, ''),
 ('ilgwu', 'Union-made (ILGWU)', 'pre-1995', 20, 60, 'Womens; tag proves US-made and era'),
 ('gunne sax', 'Gunne Sax', '1970s-1980s', 60, 250, 'Prairie dresses'),
 ('jessica mcclintock', 'Jessica McClintock', '1980s-1990s', 40, 150, ''),
 ('limited too', 'Limited Too', '1990s-2000s', 15, 50, 'Y2K'),
 ('express tricot', 'Express Tricot', '1990s', 15, 50, ''),
 ('made in usa', 'various', 'pre-2000 likely', 10, 40, 'Weak signal alone; combine with stitch');
