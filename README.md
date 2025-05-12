# 🎟️ TibaSpark Ticket Validator

This Python script automates the validation of parking tickets through the [TibaSpark](https://spark-cloud.tibaparking.net/) eValidation system. Built with Selenium WebDriver, it allows parking operators to streamline repetitive manual validations with reliability and precision.

---

## 📸 Screenshot

![TibaSpark Validation Interface](./assets/Screenshot%202025-05-12%20at%2011.14.28 AM.png)
![TibaSpark Validation Interface](./assets/Screenshot%202025-05-12%20at%2011.15.42 AM.png)


---

## 📌 Features

- 🔐 Automated login to the TibaSpark portal
- 🧠 Smart retry system for stale or missing elements
- 🕒 Elapsed time checking before validation
- ⏱️ Auto wait and resume on validation restrictions
- ❌ Graceful handling of failed validations and session interruptions

---

## 📦 Requirements

- Python 3.8+
- Google Chrome
- ChromeDriver (installed automatically)

### Install dependencies:

```bash
pip install selenium chromedriver-autoinstaller pytz
