cat > README.md << 'EOF'
# 🚚 Shipment Rate Comparator

An autonomous web agent that compares shipping rates across FedEx, UPS, and USPS using the TinyFish Web Agent API.

## ✨ Features

- **Multi-Carrier Comparison**: Fetch rates from FedEx, UPS, and USPS simultaneously
- **Real-time Rate Fetching**: Gets actual rates from carrier websites
- **Smart Recommendations**: Automatically identifies cheapest, fastest, and best value options
- **Beautiful CLI Interface**: Colored output with formatted tables
- **Mock Mode**: Test without API credentials (great for development)
- **Error Handling**: Robust error management with retry logic

## 📋 Prerequisites

- Python 3.8 or higher
- TinyFish API key (optional - mock mode works without it)

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