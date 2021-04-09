# funciona OK!

import pandas as pd
import sqlite3


# establish database connection
conn = sqlite3.connect('zidian_cn_pro')
# save sqlite table in a text file
df = pd.read_sql('SELECT * from hanzi', conn)
# write DataFrame to CSV file
df.to_csv('hanzi.csv', index = False)
