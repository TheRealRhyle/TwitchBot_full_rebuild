from random import choice, randint

def quote(message, c, conn):
    
    if "!quote" in message.lower():
        # Flow for Create, Modify, Delete
        try:
            command, quote = message.split(" ",1)
            # Create
            if quote.split(" ", 1)[0] == "add":
                rowid = c.execute('select count(*) from Quotes').fetchone()[0]+1
                c.execute("insert into Quotes values (:rowid, :quote)",{'rowid': rowid,'quote': quote.split(' ', 1)[1]})
                # print(f"Adding quote: {quote.split(' ', 1)[1]}")
                conn.commit()
                return f"Added quote: {quote.split(' ', 1)[1]} at index {rowid}."
            # Modify
            elif quote.split(" ", 1)[0] == "modify":
                rowid = quote.split(" ",2)[1]
                newQuote = quote.split(" ",2)[2]
                c.execute("update Quotes set Quote = (:newQuote) where id = (:rowid)",{'rowid':rowid, 'newQuote': newQuote})
                # print(f"Modifying quote: {quote.split(' ', 1)[1]}")
                conn.commit()
                return f"Modified quote: {quote.split(' ', 1)[1]} at index {rowid}"
            # Delete
            elif quote.split(" ", 1)[0] == "delete":
                rowid = quote.split(" ",2)[1]
                c.execute("delete from Quotes where ID = :rowid",{'rowid':rowid})
                # print(f"Deleting quote: {quote.split(' ', 1)[1]}")
                conn.commit()
                return f"Deleted quote: {quote.split(' ', 1)[1]} from index {rowid}"
            # List Quotes
            #TODO Make the list print to an HTML file or some such on a website.
            # elif quote.split(" ", 1)[0] == "list":
            #     all_quotes = c.execute('select Quote from Quotes').fetchall()
            #     all_quotes = [quote[0] for quote in all_quotes]
            #     print(all_quotes)
            # Create w/o Add
            else:
                rowid = c.execute('select count(*) from Quotes').fetchone()[0]+1
                c.execute("insert into Quotes values (:rowid, :quote)",{'rowid': rowid,'quote': quote})
                # print(f"Adding quote: {quote.split(' ', 1)[1]}")
                conn.commit()
                return f"Added quote: {quote.split(' ', 1)[1]} at index {rowid}."
            
        except:
            # Read from database
            total_quotes = c.execute('select count(*) from Quotes').fetchone()[0]
            rowid = randint(1,total_quotes)
            ret_quote = c.execute("select Quote from Quotes where ID = :rowid", {'rowid': rowid}).fetchone()[0]
            # print(ret_quote)
            return f"{rowid}. {ret_quote}" 

if __name__ == "__main__":
    import loader
    quotes = [
    "The lion, the witch, and the AUDACITY of this bitch",
    "Ex-fucking-scuse me?"
    ]
    conn, c = loader.loaddb()
    quote(f"!quote",c, conn)
    