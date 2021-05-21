'SELECT allquotes.stock AS allquotes_stock, 
        allquotes.close AS allquotes_close, 
        allquotes.timestamp AS allquotes_timestamp, 
        allquotes.volume AS allquotes_volume 
FROM allquotes
WHERE allquotes.timestamp >= %(timestamp_1)s AND allquotes.timestamp <= %(timestamp_2)s'