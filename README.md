# 🚚 Shipment Rate Comparator

An autonomous web agent that compares shipping rates across FedEx, UPS, and USPS using the TinyFish Web Agent API.

## 🎯 What It Does

- Automatically navigates carrier websites
- Fills out shipping forms with package details
- Extracts real-time shipping rates
- Compares prices and delivery times
- Recommends cheapest and fastest options

## 🏆 Hackathon Fit

This project demonstrates:
- ✅ Real work on live websites
- ✅ Multi-step workflows (navigation → form fill → extraction)
- ✅ Session management
- ✅ Clear business value (saves hours of manual work)

## 📋 Prerequisites

- Python 3.8+
- TinyFish API key (get it from [tinyfish.ai](https://www.tinyfish.ai))

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/BigMouse-Bot/shipment-rate-comparator.git
cd shipment-rate-comparator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your TinyFish API key