
from service import calculate_module_stat, get_supplies_stat, get_usage_stat, plot_all_usages_pie, plot_both_stat, plot_usage_pie


stat, ideal_stat = calculate_module_stat()
usages = {category: get_usage_stat(category, month='currMonth') for category in ['Module', 'Turret', 'Hull', 'Mode']}
print(usages)
plot_all_usages_pie(usages)
