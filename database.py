import MySQLdb

class Database:
    """
        Contains variable for our flask app database connection

    """
    def __init__(self):
        self.database = MySQLdb.connect(host='localhost', user='root',
                                        passwd='con162ess', db='teamdata')

    def add_creds(self, service, addr, user, password):
        """
            Function to add to our database of user credentials

            :param service: the service the password is for
            :param addr: the ip address the password is from
            :param user: the username that pairs with the password
            :param password: the password for the user
        """
        team = addr.split('.')[2]
        self.database.execute("INSERT INTO creds (%s, %s, %s, %s)",
                              service, team, user, password)
        self.database.commit()
