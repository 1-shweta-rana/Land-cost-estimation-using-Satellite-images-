from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
from utils import extract_lat_long_from_data
import pandas
import time

def sel_setup()-> webdriver.Chrome:
    print("Setting up headless driver...")
    # Headless driver setup dawg
    options = webdriver.ChromeOptions()

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--window-size=1280,1024")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install(), options=options))
    driver.set_page_load_timeout(20)
    print("Driver setup complete")
    return driver

def extract_and_save_with_id(driver:webdriver.Chrome, land_id:int,  data:pandas.DataFrame, output_dir:str = "./images/") -> None:
    
    lat_long_dict = extract_lat_long_from_data(data, land_id)
    if not lat_long_dict:
        return
    url = f"https://www.1acre.in/@{lat_long_dict["lat"]}-{lat_long_dict["long"]}-17m/data-!land{land_id}"
    output_path = f"./images/{land_id}.png"

    print(f"checking url: {url}", "\n")
    try:

        driver.get(url)
        time.sleep(5)
        ELEMENTS_TO_HIDE_JS = """

    function hideNonMapElements() {
        // Get the map canvas first
        const mapCanvas = document.querySelector('.mapboxgl-canvas');
        
        if (!mapCanvas) {
            return "Map canvas not found yet";
        }
        
        // 1. Remove headers
        const headers = document.querySelectorAll('header, [class*="header"]');
        headers.forEach(header => {
            header.style.display = 'none';
            header.style.visibility = 'hidden';
        });
        
        // 2. Remove bottom navigation
        const bottomNav = document.querySelector('nav, [class*="bottom-0"]');
        if (bottomNav) {
            bottomNav.style.display = 'none';
            bottomNav.style.visibility = 'hidden';
        }
        
        // 3. CRITICAL: Make sure the map canvas and its containers fill the ENTIRE screen
        const mapContainers = document.querySelectorAll('.mapboxgl-canvas, .mapboxgl-map, .flex-grow, .relative');
        mapContainers.forEach(container => {
            Object.assign(container.style, {
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100vw',
                height: '100vh', // This ensures full height
                zIndex: '9999'
            });
        });
        
        // 4. Force the map canvas to resize to full viewport
        if (mapCanvas) {
            // Force resize of the map canvas itself
            mapCanvas.style.width = '100vw';
            mapCanvas.style.height = '100vh';
            mapCanvas.style.position = 'fixed';
            mapCanvas.style.top = '0';
            mapCanvas.style.left = '0';
            
            // Trigger a resize event for Mapbox to redraw
            if (window.mapboxgl && mapCanvas._mapboxglMap) {
                mapCanvas._mapboxglMap.resize();
            }
        }
        
        // 5. Hide all other body children
        const allElements = document.querySelectorAll('body > *');
        allElements.forEach(element => {
            if (!element.contains(mapCanvas) && element !== mapCanvas) {
                element.style.display = 'none';
                element.style.visibility = 'hidden';
            }
        });
        
        // 6. Remove map controls
        const controls = document.querySelector('.mapboxgl-control-container');
        if (controls) controls.style.display = 'none';
        
        // 7. CRITICAL: Reset body and html to remove any padding/margin
        document.body.style.margin = '0';
        document.body.style.padding = '0';
        document.body.style.overflow = 'hidden';
        document.body.style.height = '100vh';
        document.body.style.width = '100vw';
        
        document.documentElement.style.margin = '0';
        document.documentElement.style.padding = '0';
        document.documentElement.style.overflow = 'hidden';
        document.documentElement.style.height = '100vh';
        document.documentElement.style.width = '100vw';
        
        return "Map should now fill entire screen without white bars";
    }
    
    // Try multiple times
    setTimeout(hideNonMapElements, 500);
    setTimeout(hideNonMapElements, 2000);
    setTimeout(() => {
        hideNonMapElements();
        // One more attempt after a longer delay to catch any late-rendering elements
        setTimeout(hideNonMapElements, 1000);
    }, 4000);
    
    return "Started full-screen map cleanup";
"""
        driver.execute_script(ELEMENTS_TO_HIDE_JS)
        
        time.sleep(2)

        driver.save_screenshot(output_path)

    except Exception as e:
        print("Error: ","\n", f"{e}","\n",f"{land_id=}")