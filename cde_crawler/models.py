from os import getenv

import peewee
import peewee_async


database = {
    'database': getenv('DB_DATABASE'),
    'user': getenv('DB_USER'),
    'password': getenv('DB_PASSWORD'),
    'host': getenv('DB_HOST'),
    'port': getenv('DB_PORT', '5432'),
}

database = peewee_async.PostgresqlDatabase(**database)


class CDE(peewee.Model):
    code = peewee.TextField()
    name = peewee.TextField()
    drug_type = peewee.TextField(null=True)
    apply_type = peewee.TextField(null=True)
    reg_type = peewee.TextField(null=True)
    pharm_name = peewee.TextField(null=True)
    accept_date = peewee.DateField(null=True)

    class Meta:
        database = database
        indexes = (
            (('code', ), True),
        )


if __name__ == '__main__':
    CDE.create_table(fail_silently=True)
