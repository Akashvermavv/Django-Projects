from django.db import models


class Toppings(models.Model):
    topping_name = models.CharField(max_length=150,)

    def __str__(self):
        return str(self.topping_name)


class Sizes(models.Model):
    pizza_size = models.CharField(max_length=150, )

    def __str__(self):
        return str(self.pizza_size)

pizza_type =(
    ('Square','square'),
    ('Regular','regular'),
)


class Pizza(models.Model):
    pizza_type = models.CharField(max_length=150,choices=pizza_type)
    size_type = models.ForeignKey(Sizes,on_delete=models.CASCADE,)
    topping_type = models.ManyToManyField(Toppings,)


    def __str__(self):
        return str(self.pizza_type)


