import peewee
import peewee_async
from .database_settings import database


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
            (('code', 'accept_date'), True),
        )


if __name__ == '__main__':
    CDE.create_table(fail_silently=True)
