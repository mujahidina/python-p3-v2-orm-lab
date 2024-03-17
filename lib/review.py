from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )
    def get_year(self):
        return self._year
    
    def set_year(self, year):
        """Setter method for the year attribute."""
        if isinstance(year, int) and year >= 2000:
            self._year = year
        else:
            raise ValueError("Year must be of type integer and greater than or equal to 2000.")

    year = property(get_year, set_year)

    def get_summary(self):
        return self._summary
    
    def set_summary(self, summary):
        if isinstance(summary, str) and len(summary) > 0:
            self._summary = summary
        else:
            raise ValueError("summary must be a non-empty string.")
    summary = property(get_summary, set_summary)

    
    def get_employee_id(self):
        return self._employee_id

    def set_employee_id(self, employee_id):
        if Employee.find_by_id(employee_id) is None:
            raise ValueError("Invalid employee_id. Employee does not exist.")
        else:
            self._employee_id = employee_id
    employee_id = property(get_employee_id, set_employee_id)

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            values = (self.year, self.summary, self.employee_id)
            CURSOR.execute(sql, values)
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            sql = """
                UPDATE reviews
                SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            """
            values = (self.year, self.summary, self.employee_id, self.id)
            CURSOR.execute(sql, values)
            CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Return a Review instance having the attribute values from the table row."""
        review_id, year, summary, employee_id = row
        if review_id in cls.all:
            return cls.all[review_id]
        else:
            review = cls(year, summary, employee_id, id=review_id)
            cls.all[review_id] = review
            return review

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = """
            SELECT * FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
            return None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        self.save()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        sql = """
            DELETE FROM reviews WHERE id = ?
        """
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del Review.all[self.id]
        self.id = None
    
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        review = cls.all.get(row[0])
        if review:
            # ensure attributes match row values in case local instance was modified
            review.year = row[1]
            review.summary = row[2]
            review.employee_id = row[3]
        else:
            # not in dictionary, create new instance and add to dictionary
            review = cls(row[1], row[2], row[3])
            review.id = row[0]
            cls.all[review.id] = review
        return review
   

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = """
            SELECT * FROM reviews
        """
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
