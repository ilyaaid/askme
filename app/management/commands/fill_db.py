from django.core.management.base import BaseCommand



def fill_with_ratio(ratio):
    pass



class Command(BaseCommand):
    help = "Filling the database"

    def add_arguments(self, parser):
        parser.add_argument("ratio", type=int, help="Введите коэффициент заполнения")

    def handle(self, *args, **options):
        ratio = options.get('ratio')
        self.stdout.write("Коэффициент: " + str(ratio))
        fill_with_ratio(ratio)




