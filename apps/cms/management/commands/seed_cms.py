from django.core.management.base import BaseCommand

from apps.cms.defaults import default_cms_content
from apps.cms.services import write_cms_content


class Command(BaseCommand):
    help = "Seed website CMS content from default JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing CMS content.",
        )

    def handle(self, *args, **options):
        from apps.cms.models import CmsContentStore, SINGLETON_PK

        exists = CmsContentStore.objects.filter(pk=SINGLETON_PK).exists()
        if exists and not options["force"]:
            self.stdout.write("CMS content already exists. Use --force to overwrite.")
            return

        content = write_cms_content(default_cms_content())
        self.stdout.write(self.style.SUCCESS(f"Seeded CMS ({len(content.get('rooms', []))} rooms)."))
