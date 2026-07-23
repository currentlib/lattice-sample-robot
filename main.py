from rpa_core import BasePerformer, BusinessRuleException

class InvoicePerformer(BasePerformer):
    QUEUE_NAME = "Invoices"

    def setup(self):
        self.log("Initializing robot state and checking assets...")

    def process(self, item):
        invoice_num = item.data.get("invoice_num")
        amount = item.data.get("amount", 0)
        self.log(f"Processing invoice #{invoice_num} for ${amount}")

        if amount > 5000:
            raise BusinessRuleException(f"Invoice amount ${amount} requires manual approval")

        asset = self.get_asset("TestAsset")
        self.log(f"ASSET VALUE: {asset}")

        self.log(f"Invoice #{invoice_num} processed successfully!")

    def cleanup(self):
        self.log("Closing robot session.")

if __name__ == "__main__":
    robot = InvoicePerformer()
    robot.run()
