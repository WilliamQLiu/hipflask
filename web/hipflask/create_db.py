from hipflask import db, Buzz


print("Running create data in database script")
db.drop_all()  # Drop all existing database tables
db.create_all()  # Create database and database tables

#Insert some fake data
buzz1 = Buzz(url="http://www.google.com")
buzz2 = Buzz(url="http://www.jobwaffle.com")
buzz3 = Buzz(url="http://commandpages.com")
db.session.add(buzz1)
db.session.add(buzz2)
db.session.add(buzz3)

# Commit the changes
db.session.commit()

print("Finished running create data in database script")
