"""
CREATE TABLE Word (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sWord TEXT,
    sType TEXT,
    isIgnore INTEGER,
    imgData BLOB
);


CREATE TABLE FontSpecial (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sWord TEXT,
    isIgnore INTEGER,
    sfile TEXT
);
"""

"""
CREATE TABLE SountSpecial (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    sWord TEXT,
    isIgnore INTEGER
);
"""
"""
CREATE TABLE [normal_word] (
	[ID] integer PRIMARY KEY AUTOINCREMENT, 
	[sWord] text
)

"""