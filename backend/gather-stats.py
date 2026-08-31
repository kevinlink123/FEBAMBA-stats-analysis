from datetime import datetime
import sys
from uiautomator2 import Direction
import uiautomator2 as u2

# TODO: Constants (MOVE TO THEIR OWN FILE)
PACKAGE_NAME = "com.indalweb.aficionCABB"
SEARCH_BAR_TEAM_NAME = "all boys saavedra"
TEAM_NAME = "LIGA PROXIMO MASCULINO FORMATIVAS 2026"


# Conéctate al dispositivo (si solo hay uno conectado)
d = u2.connect()
print(d.device_info)  

# Inicia la app CABB (deteniéndola antes para empezar desde el principio)
d.app_start(PACKAGE_NAME, stop=True)

# Espera unos segundos para que la app cargue
d.sleep(10)
print("App iniciada correctamente.")

# Obtener información de la pantalla actual
current_app = d.app_current()
print(f"App actual: {current_app}")

# Wait for header to appear (first load)
hamburguer_menu = d.xpath("(//android.view.View)[9]").get(timeout=10)

permisos = d.shell(f"dumpsys package {PACKAGE_NAME} | grep 'android.permission.WRITE_EXTERNAL_STORAGE'").output
if "granted=true" not in permisos:
    print("⚠️ La app no tiene permiso de escritura. Concediendo...")
    # Otorgar permiso manualmente
    d.shell(f"pm grant {PACKAGE_NAME} android.permission.WRITE_EXTERNAL_STORAGE")

# Search for team to stract data
team_baner = d.xpath(f'//*[@text="{TEAM_NAME}"]').get(timeout=10)
team_baner.click()

# Go to matchs section
matchs_section_button = d.xpath('//*[@text=" PARTIDOS"]').get(timeout=10)
matchs_section_button.click()

start_date_picker_button = d.xpath('//android.widget.DatePicker').get()
start_date_picker_button.click()

actual_month_str = d.xpath('//android.view.View[@text="1"]').get().info.get('contentDescription')
if not actual_month_str:
    print("No DateTime Picker displayed!")
    sys.exit("Element Not Found!")

print(f"📅 Mes actual: {actual_month_str}")

# Convertir "01 July 2026" a objeto datetime
actual_month = datetime.strptime(actual_month_str, "%d %B %Y")
print(f"📅 Mes actual (datetime): {actual_month}")

# Calcular cuántos meses hay hasta enero
month_january = datetime(actual_month.year, 1, 1)

# Calcular la diferencia en meses
months_to_go_back = (actual_month.year - month_january.year) * 12 + (actual_month.month - month_january.month)
print(f"🔙 Meses a retroceder: {months_to_go_back}")

back_chevron = d.xpath('//*[@content-desc="Previous month"]').get()
for i in range(months_to_go_back):
    back_chevron.click()

first_january_button = d.xpath('//*[@content-desc="01 January 2026"]').get()
first_january_button.click()

date_picker_set_button = d.xpath('//android.widget.Button[@text="SET"]').get()
date_picker_set_button.click()

is_no_data_banner_gone = d.xpath('//*[@text="No hay datos"]').wait_gone(timeout=15)

if not is_no_data_banner_gone:
    print("'No Data' banner still displayed!")
    sys.exit("Error while selecting date!")

# Now we should be seing all the mathces till today
# TODO: Refactor this to go through all the matches and not just the first one
matches = d.xpath(f'//android.view.View[@text="{SEARCH_BAR_TEAM_NAME.upper()}"]').get()
match_datetime = d.xpath('(//android.view.View)[59]/*[2]').get()
print(match_datetime.info.get('text'))
matches.click()

match_ended = d.xpath('//android.view.View[@text="FINAL DEL PARTIDO"]').wait(timeout=15)
if not match_ended:
    print("The match is not ended or you are not in a match screen!")
    sys.exit("Error while selecting match!")

stats_screen_button = d.xpath('//android.view.View[@text="ESTADÍSTICAS"]').get()
stats_screen_button.click()

download_excel_button = d.xpath('//android.widget.Button[@text="download outline EXCEL"]').get()
download_excel_button.click()

# Now we should be in google sheets app
# THIS PART WORKS ONLY FOR GOOGLE SHEETS APP
more_options_sheets_button = d.xpath('//*[@content-desc="More options"]').get()
more_options_sheets_button.click()

share_and_export_button = d.xpath('//android.widget.TextView[@text="Share & export"]').get()
share_and_export_button.click()

save_as_button = d.xpath('//android.widget.TextView[@text="Save As"]').get()
save_as_button.click()

csv_file_selector = d.xpath('//android.widget.CheckedTextView[@text="CSV (current sheet)"]').get()
csv_file_selector.click()

file_selector_ok_button = d.xpath('//android.widget.Button[@text="OK"]').get()
file_selector_ok_button.click()

location_selector_device = d.xpath('//android.widget.CheckedTextView[@text="Device"]').get()
location_selector_device.click()

location_selector_save_button = d.xpath('//android.widget.Button[@text="Save"]').get()
location_selector_save_button.click()

# Now we should be on the default files app
stats_file_name = "estadisticaPartido_202603623.csv"

# TODO: Finish this function to mark teams as favorites
def add_team_to_main_screen():
    sidebar_search_button = d.xpath('//*[@content-desc="search outline"]').get(timeout=15)
    if not sidebar_search_button:
        print("No search button displayed!")
        sys.exit("Element Not Found!")

    sidebar_search_button.click()

    d.sleep(2)
    search_bar = d.xpath("//android.widget.EditText")
    if search_bar.exists:
        search_bar.click()
        d.sleep(2)
        d.send_keys(SEARCH_BAR_TEAM_NAME)
    else:
        print("❌ No se encontró el campo de búsqueda")
        sys.exit(1)

    search_bar = d.xpath('//*[@text="BUSCAR"]').click_exists(timeout=10)
    d.sleep(3)





# Hacer una captura de pantalla para verificar que la app está visible
d.screenshot("screenshots/test_screenshot.png")
print("📸 Captura de pantalla guardada como 'test_screenshot.png'")