import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def auto_fill_job_application(job_url, candidate_profile):
    """Launches Chrome, auto-populates candidate details and attaches the resume,
    then holds for human confirmation before submission.
    """
    print(f"\n🚀 Launching Browser for: {job_url}")
    print("⚡ Populating application fields...")

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get(job_url)

        time.sleep(2)

        # Populate Form Fields
        try:
            name_inputs = driver.find_elements(
                By.XPATH,
                "//input[contains(@name, 'name') or contains(@id, 'name') or contains(@placeholder, 'Name')]",
            )
            for inp in name_inputs:
                inp.clear()
                inp.send_keys(candidate_profile.get("full_name", ""))
                print(
                    f"  🎉 Auto-filled field [name]: {candidate_profile.get('full_name', '')}"
                )
        except Exception:
            pass

        # Resume Attachment
        resume_path = candidate_profile.get("resume_path", "")
        if resume_path and os.path.exists(resume_path):
            try:
                file_input = driver.find_element(
                    By.XPATH, "//input[@type='file']"
                )
                file_input.send_keys(os.path.abspath(resume_path))
                print("  📎 Attached Resume PDF successfully.")
            except Exception:
                pass

        # Assisted Mode UI
        print("\n" + "=" * 65)
        print("👀 ASSISTED MODE ACTIVE:")
        print("1. Review the open browser window.")
        print("2. Check the auto-filled details and edit if needed.")
        print("3. Click SUBMIT manually on the webpage.")
        print("=" * 65)

        # Fully Translated to Professional English
        input("\n👉 After submitting on the webpage, press [ENTER] in this terminal to complete...")
        print("✅ Completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Automation Error: {e}")
        return False
    finally:
        if driver:
            driver.quit()