Vegetable Vendor Door-Delivery System__ This web-based application, built with Flask, HTML, CSS, and JavaScript, enables a small-scale vegetable vendor to efficiently manage door-delivery services. The system incorporates various design patterns for modularity, scalability, and maintainability.

Features

Daily Inventory: Maintain a daily list of available vegetables. Order Management: Accept customer orders with individual quantities, assigning unique order numbers for tracking. Billing: Generate bills for orders exceeding Rs. 100. Payment Confirmation: Confirm payments through notifications to both customers and the vendor. Order Modification: Disable order modification after payment confirmation. Real-time Updates: Communicate vegetable availability to customers during ordering. Delivery Notifications: Notify customers when orders are ready, providing tentative delivery times.

Design Patterns Used

Singleton: Ensure a single instance of essential components like the order manager. Observer: Notify customers and the vendor of real-time changes in vegetable availability. Builder: Facilitate flexible order construction with varied vegetables and quantities. Strategy: Implement diverse payment methods for interchangeability and extensibility. Command: Encapsulate requests for operations like updating stock and generating bills. Decorator: Dynamically add features to orders, such as discounts or delivery charges. State: Manage the order lifecycle, transitioning between states like "placed," "confirmed," and "delivered."

Getting Started

Clone the repository: git clone https://github.com/your-username/vegetable-delivery-system.git

Install dependencies: pip install -r requirements.txt

Run the application: python run.py

Access the application at http://localhost:5000.

Contributions Contributions are welcome! Feel free to submit issues and pull requests.

License This project is licensed under the MIT License - see the LICENSE file for details.
