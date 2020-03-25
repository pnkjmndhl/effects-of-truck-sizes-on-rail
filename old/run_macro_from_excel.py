import os, os.path
import win32com.client

filename = "UTK_TruckingCostModel_KNorris_Version1.xlsm"
modulename = "Module1"
macroname = "macroAutorunTruckingCostModel"

#constants
#fuel cost
fuel_price_p_gallon =
loaded_truck_miles_p_gallon =
empty_truck_miles_p_gallon =
percent_time_loaded =
percent_time_empty =
round_trip_travel_dist =
#labor cost
round_trive_driving_time =
unloading_time =
loading_time =
dwell_time =
driver_labor_cost_phr =
#tyre cost
tractor_tire_cost_ptyr =
trailor_tire_cost_ptyr =
tractor_tire_miles_ptyr =
trailor_tire_miles_ptyr =
#maintenance and repair cost
base_repair_cost_pmile =
#equipment cost
purchse_price_of_tractor =
purchase_price_of_trailor =
useful_life_of_tractor =
useful_life_of_trailor =
interest_rate =
#license fee
annual_license_fee =
number_of_tractors_and_trailors_in_fleet =
annual_miles =
#management and overhead cost
overhead_cost_rate =
#insurance cost
insurance_premium =


xl=win32com.client.Dispatch("Excel.Application")
xl.Application.Visible = True
xl.ScreenUpdating = False

wb = xl.Workbooks.Open(os.path.abspath(filename))
sheet = wb.Worksheets(1)

def run_model(payload,tractor_wt,trailer_wt):
    sheet.Cells(6,4).Value = payload
    sheet.Cells(7,4).Value = tractor_wt
    sheet.Cells(8,4).Value = trailer_wt

    sheet.Cells(10,4).Value = fuel_price_p_gallon
    sheet.Cells(11,4).Value = loaded_truck_miles_p_gallon
    sheet.Cells(12,4).Value = empty_truck_miles_p_gallon
    sheet.Cells(13,4).Value = percent_time_loaded
    sheet.Cells(14,4).Value = percent_time_empty
    sheet.Cells(15,4).Value = round_trip_travel_dist

    sheet.Cells(17,4).Value = round_trive_driving_time
    sheet.Cells(18,4).Value = unloading_time
    sheet.Cells(19,4).Value = loading_time
    sheet.Cells(21,4).Value = dwell_time
    sheet.Cells(22,4).Value = driver_labor_cost_phr

    sheet.Cells(25,4).Value = tractor_tire_cost_ptyr
    sheet.Cells(26,4).Value = trailor_tire_cost_ptyr
    sheet.Cells(27,4).Value = tractor_tire_miles_ptyr
    sheet.Cells(28,4).Value = trailor_tire_miles_ptyr

    sheet.Cells(30,4).Value = base_repair_cost_pmile

    sheet.Cells(6,8).Value = purchse_price_of_tractor
    sheet.Cells(7,8).Value = purchase_price_of_trailor
    sheet.Cells(8,8).Value = useful_life_of_tractor
    sheet.Cells(9,8).Value = useful_life_of_trailor
    sheet.Cells(10,8).Value = interest_rate

    sheet.Cells(12,8).Value = annual_license_fee
    sheet.Cells(13,8).Value = number_of_tractors_and_trailors_in_fleet
    sheet.Cells(14,8).Value = annual_miles

    sheet.Cells(16,8).Value = overhead_cost_rate

    sheet.Cells(18,8).Value = insurance_premium

    xl.Application.Run(filename+"!"+ modulename+"."+macroname)

    total_trucking_cost = sheet.Cells(26,8).Value
    total_trucking_cost_ph = sheet.Cells(27,8).Value
    total_trucking_cost_pm = sheet.Cells(28,8).Value
    total_trucking_cost_pt = sheet.Cells(29,8).Value
    total_trucking_cost_pltm = sheet.Cells(30,8).Value

    return total_trucking_cost