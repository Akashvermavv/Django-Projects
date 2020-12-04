from django.contrib import admin
from .models import (
                        Pizza,
                        Toppings,
                        Sizes
                    )


admin.site.register(Pizza)
admin.site.register(Toppings)
admin.site.register(Sizes)