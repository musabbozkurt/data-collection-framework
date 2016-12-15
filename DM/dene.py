import datetime
userInDate = input("Type Date yyyy-mm-dd: ")
try: # strptime throws an exception if the input doesn't match the pattern
    print(datetime.datetime.strptime(userInDate, '%Y-%m-%d'))
except ValueError:
    print ("Invalid Input. Please try again.\n")
else:
    isValid=True
    d = userInDate