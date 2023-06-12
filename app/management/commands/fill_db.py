from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Filling the database"

    # def add_arguments(self, parser):
    #     parser.add_argument("ratio", nargs="+", type=int)

    def handle(self, *args, **options):
        print("hello!")

