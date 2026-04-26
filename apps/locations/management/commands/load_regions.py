"""
Django management command to load region and city seed data
Usage: python manage.py load_regions
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.locations.models import Region, City
from scripts.seed_data import REGIONS_DATA, CITIES_DATA


class Command(BaseCommand):
    help = 'Load regions and cities for Uzbekistan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing regions and cities before loading',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        should_clear = options.get('clear', False)

        # Clear existing data if requested
        if should_clear:
            self.stdout.write('Clearing existing regions and cities...')
            City.objects.all().delete()
            Region.objects.all().delete()

        # Load regions
        self.stdout.write('Loading regions...')
        regions_created = 0
        for region_data in REGIONS_DATA:
            region, created = Region.objects.get_or_create(
                code=region_data['code'],
                defaults={
                    'name_uz': region_data['name_uz'],
                    'name_ru': region_data['name_ru'],
                    'name_en': region_data['name_en'],
                    'delivery_days_min': region_data['delivery_days_min'],
                    'delivery_days_max': region_data['delivery_days_max'],
                }
            )
            if created:
                regions_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created region: {region.name_en}')
                )
            else:
                self.stdout.write(f'⊝ Region already exists: {region.name_en}')

        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {regions_created} new regions')
        )

        # Load cities
        self.stdout.write('\nLoading cities...')
        cities_created = 0
        for city_data in CITIES_DATA:
            try:
                region = Region.objects.get(code=city_data['region_code'])
                city, created = City.objects.get_or_create(
                    region=region,
                    name_en=city_data['name_en'],
                    defaults={
                        'name_uz': city_data['name_uz'],
                        'name_ru': city_data['name_ru'],
                        'is_hub': city_data['is_hub'],
                    }
                )
                if created:
                    cities_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created city: {region.name_en} - {city.name_en}'
                        )
                    )
                else:
                    self.stdout.write(
                        f'⊝ City already exists: {region.name_en} - {city.name_en}'
                    )
            except Region.DoesNotExist:
                raise CommandError(f'Region with code {city_data["region_code"]} not found')

        self.stdout.write(
            self.style.SUCCESS(f'\nCreated {cities_created} new cities')
        )
        self.stdout.write(
            self.style.SUCCESS('\n✓ Successfully loaded all seed data!')
        )
