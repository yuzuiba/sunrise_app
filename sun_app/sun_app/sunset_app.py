import requests
import customtkinter as custom
from tkinter import StringVar
import datetime

global_font = ("Courier", 13)
global_font_bold = ("Courier", 14, "bold")
title_font = ("Courier", 22, "bold")

headers = {
    "x-rapidapi-key": "",
    "x-rapidapi-host": "sunrise-sunset-times.p.rapidapi.com"
}

custom.set_appearance_mode("light")
custom.set_default_color_theme("blue")

def GetCoordinates(city: str):
    coor_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en"
    resp = requests.get(coor_url).json()
    lat = resp["results"][0]["latitude"]
    lon = resp["results"][0]["longitude"]
    city_name = resp["results"][0].get("name", city)
    country = resp["results"][0].get("country", "")
    location_name = f"{city_name}, {country}" if country else city_name
    return float(lat), float(lon), location_name

def GetSunTimes(lat: float, lon: float, date: str, tz_id: str):
    url = "https://sunrise-sunset-times.p.rapidapi.com/getSunTimes"
    params = {"latitude": lat, "longitude": lon, "date": date, "timeZoneId": tz_id}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    j = r.json()
    return {"sunrise": j.get("sunrise"), "sunset": j.get("sunset")}

class MainGUI(custom.CTk):
    def __init__(self):
        super().__init__()
        # Window Title and Size
        self.title("Sunrise and Sunset Times")
        self.geometry("1100x620")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)


        # Frame
        main = custom.CTkFrame(self, fg_color="#f8cadd", corner_radius=0)
        main.grid(row=0, column=0, sticky="nswe", padx=12, pady=12)
        main.grid_columnconfigure(0, weight=1)

        # Title
        custom.CTkLabel(main, text="Sunrise and Sunset Times", font=title_font, text_color="black").grid(row=0, column=0, pady=(10, 6))

        # Frame for input controls
        input_frame = custom.CTkFrame(main, fg_color="#f8cadd")
        input_frame.grid(row=1, column=0, sticky="we", pady=6)
        for i in range(4):
            input_frame.grid_columnconfigure(i, weight=1)

        # Where you input the location
        self.location_entry = custom.CTkEntry(input_frame, placeholder_text="Input location here", font=global_font)
        self.location_entry.grid(row=0, column=0, padx=8, pady=6, sticky="we")

        # Combo box with timezones
        # EST and CET get converted into their corresponding UTC equivalents which is recognized by the API
        self.timezone_box = custom.CTkComboBox(input_frame, values=["UTC+8", "UTC+0", "EST (UTC-5)", "CET (UTC+1)"], width=150, font=global_font, dropdown_font=global_font)
        self.timezone_box.set("UTC+8")
        self.timezone_box.grid(row=0, column=1, padx=8, pady=6)

        # WHere you input the date
        self.date_var = StringVar()
        self.date_var.set(str(datetime.date.today()))

        self.date_entry = custom.CTkEntry(input_frame, textvariable=self.date_var, placeholder_text="DATE (YYYY-MM-DD)", font=global_font)
        self.date_entry.grid(row=0, column=2, padx=8, pady=6, sticky="we")

        # Submit button
        self.submit_btn = custom.CTkButton(input_frame, text="Submit", command=self.submit, font=global_font_bold)
        self.submit_btn.grid(row=0, column=3, padx=8, pady=6)

        # Panel for sunset/sunrise
        self.sun_panel = custom.CTkFrame(main, fg_color="#ffffff", corner_radius=18, height=160)
        self.sun_panel.grid(row=2, column=0, sticky="we", padx=16, pady=(10, 6))
        self.sun_panel.grid_propagate(False)

        # Initializes the variables for text to be displayed in sunset/sunrise panel
        self.sun_title_var = StringVar()
        self.sun_text_var = StringVar()

        # Panel Title
        custom.CTkLabel(self.sun_panel, textvariable=self.sun_title_var, font=global_font_bold, text_color="black").pack(pady=(10, 0))
       
        # Content of the sunrise/sunset panel
        self.sun_text_label = custom.CTkLabel(self.sun_panel, textvariable=self.sun_text_var, wraplength=700, justify="center", text_color="black", font=global_font)
        self.sun_text_label.pack(pady=(6, 10))

        # Panel for weather
        self.weather_panel = custom.CTkFrame(main, fg_color="#ffffff", corner_radius=18, height=160)
        self.weather_panel.grid(row=3, column=0, sticky="we", padx=16, pady=(6, 10))
        self.weather_panel.grid_propagate(False)

        # Sets the variables for weather outputs
        self.weather_title_var = StringVar()
        self.weather_text_var = StringVar()

        custom.CTkLabel(self.weather_panel, textvariable=self.weather_title_var, font=global_font_bold, text_color="black").pack(pady=(10, 0))
        custom.CTkLabel(self.weather_panel, textvariable=self.weather_text_var, font=global_font, text_color="black", wraplength=700, justify="center").pack(pady=(6, 10))

        # Returns idle text
        self.set_idle_texts()

    def set_idle_texts(self):
        self.sun_title_var.set("Sunrise & Sunset")
        self.sun_text_var.set("Enter a location and click Submit.")
        self.weather_title_var.set("Weather")
        self.weather_text_var.set("")

    def submit(self):
        self.submit_btn.configure(state="disabled", text="Working...") # Disables button after it starts working
        try: # Gets inputs for city, date and the timezone from the combo box
            city = self.location_entry.get().strip()
            date = self.date_var.get().strip()
            tz_selection = self.timezone_box.get().strip()

            tz_map = { # This is where the timezones EST and CET along with the UTC variants get mapped to UTC which is accepted by the API
                "UTC+8": "UTC+8",
                "UTC+0": "UTC+0",
                "EST (UTC-5)": "UTC-5",
                "CET (UTC+1)": "UTC+1"
            }
            tz = tz_map.get(tz_selection, "UTC+8")

            lat, lon, location_name = GetCoordinates(city) # Fetches coordinates of the inputted city
            sun = GetSunTimes(lat, lon, date, tz) # Along with teh sunrise/sunset times

            sun_title = f"Sun times for {location_name} on {date}"
            sun_lines = []
            if "sunrise" in sun:
                sun_lines.append(f"Sunrise: {sun['sunrise']}")
            if "sunset" in sun:
                sun_lines.append(f"Sunset:  {sun['sunset']}")

            self.sun_title_var.set(sun_title)
            self.sun_text_var.set("\n".join(sun_lines))

        finally:
            self.submit_btn.configure(state="normal", text="Submit")

if __name__ == "__main__":
    app = MainGUI() # Creates the GUI object
    app.mainloop() # Starts the GUI event loop
s