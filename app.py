from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import threading

app = Flask(__name__)

# Define calculation functions for EC2, RDS, and S3 (unchanged)
def calculate_ec2_cost(cost_per_vm_hour, num_vms, hours):
    return cost_per_vm_hour * num_vms * hours

def calculate_rds_cost(cost_per_db_hour, num_dbs, hours):
    return cost_per_db_hour * num_dbs * hours

def calculate_s3_cost(cost_per_gb_month, data_size_gb):
    return cost_per_gb_month * data_size_gb
    
# Initialize global variables for results and URLs
ec2_plot_url = None
rds_plot_url = None
s3_plot_url = None

@app.route("/", methods=["GET", "POST"])
def index():
    global ec2_plot_url, rds_plot_url, s3_plot_url

    ec2_total_cost_without_optimization = None
    ec2_total_cost_with_optimization = None
    ec2_cost_savings = None

    rds_total_cost_without_optimization = None
    rds_total_cost_with_optimization = None
    rds_cost_savings = None

    s3_total_cost_without_optimization = None
    s3_total_cost_with_optimization = None
    s3_cost_savings = None

    if request.method == "POST":
        try:
            # Get user input for EC2
            ec2_cost_per_vm_hour = float(request.form["ec2_cost_per_vm_hour"])
            ec2_continuous_vms = int(request.form["ec2_continuous_vms"])
            ec2_peak_vms = int(request.form["ec2_peak_vms"])
            ec2_hours = int(request.form["ec2_hours"])

            # Get user input for RDS
            rds_cost_per_db_hour = float(request.form["rds_cost_per_db_hour"])
            rds_num_dbs = int(request.form["rds_num_dbs"])
            rds_hours = int(request.form["rds_hours"])

            # Get user input for S3
            s3_cost_per_gb_month = float(request.form["s3_cost_per_gb_month"])
            s3_data_size_gb = int(request.form["s3_data_size_gb"])

            # Perform calculations in separate threads for EC2, RDS, and S3
            t_ec2 = threading.Thread(target=perform_ec2_calculations, args=(ec2_cost_per_vm_hour, ec2_continuous_vms, ec2_peak_vms, ec2_hours))
            t_rds = threading.Thread(target=perform_rds_calculations, args=(rds_cost_per_db_hour, rds_num_dbs, rds_hours))
            t_s3 = threading.Thread(target=perform_s3_calculations, args=(s3_cost_per_gb_month, s3_data_size_gb))

            t_ec2.start()
            t_rds.start()
            t_s3.start()

            # Wait for all threads to complete
            t_ec2.join()
            t_rds.join()
            t_s3.join()

            return redirect(url_for("results"))

        except ValueError:
            error_message = "Invalid input. Please enter numeric values for cost and quantities."
            return render_template("index.html", error_message=error_message)

    return render_template("index.html")

@app.route("/results", methods=["GET"])
def results():
    global ec2_plot_url, rds_plot_url, s3_plot_url

    return render_template("results.html",
                           ec2_plot_url=ec2_plot_url,
                           ec2_total_cost_without_optimization=ec2_total_cost_without_optimization,
                           ec2_total_cost_with_optimization=ec2_total_cost_with_optimization,
                           ec2_cost_savings=ec2_cost_savings,
                           rds_plot_url=rds_plot_url,
                           rds_total_cost_without_optimization=rds_total_cost_without_optimization,
                           rds_total_cost_with_optimization=rds_total_cost_with_optimization,
                           rds_cost_savings=rds_cost_savings,
                           s3_plot_url=s3_plot_url,
                           s3_total_cost_without_optimization=s3_total_cost_without_optimization,
                           s3_total_cost_with_optimization=s3_total_cost_with_optimization,
                           s3_cost_savings=s3_cost_savings)

def perform_ec2_calculations(ec2_cost_per_vm_hour, ec2_continuous_vms, ec2_peak_vms, ec2_hours):
    global ec2_plot_url, ec2_total_cost_without_optimization, ec2_total_cost_with_optimization, ec2_cost_savings

    # Calculate the total cost for EC2 without optimization
    ec2_total_cost_without_optimization = calculate_ec2_cost(
        ec2_cost_per_vm_hour, ec2_continuous_vms, ec2_hours
    )

    # Calculate the total cost for EC2 with optimization
    # Adjust the number of VMs and hours for optimization as needed
    ec2_total_cost_with_optimization = calculate_ec2_cost(
        ec2_cost_per_vm_hour, ec2_peak_vms, ec2_hours  # Adjust these values for optimization
    )

    # Calculate the cost savings for EC2
    ec2_cost_savings = ec2_total_cost_without_optimization - ec2_total_cost_with_optimization

    # Data visualization for EC2 cost comparison
    ec2_labels = ['Total Cost Without Optimization (EC2)', 'Total Cost With Optimization (EC2)']
    ec2_values = [ec2_total_cost_without_optimization, ec2_total_cost_with_optimization]

    plt.figure(figsize=(8, 6))
    plt.bar(ec2_labels, ec2_values, color=['blue', 'green'])
    plt.ylabel('Cost ($)')
    plt.title('EC2 Cost Comparison')

    # Save the EC2 plot to a BytesIO object and encode it to base64
    ec2_image = BytesIO()
    plt.savefig(ec2_image, format='png')
    ec2_image.seek(0)
    ec2_plot_url = base64.b64encode(ec2_image.getvalue()).decode()


def perform_rds_calculations(rds_cost_per_db_hour, rds_num_dbs, rds_hours):
    global rds_plot_url, rds_total_cost_without_optimization, rds_total_cost_with_optimization, rds_cost_savings

    # Calculate the total cost for RDS without optimization
    rds_total_cost_without_optimization = calculate_rds_cost(
        rds_cost_per_db_hour, rds_num_dbs, rds_hours
    )

    # Calculate the total cost for RDS with optimization (assume a 20% cost reduction)
    optimization_percentage = 0.20  # Adjust this percentage based on expected optimization results
    rds_total_cost_with_optimization = rds_total_cost_without_optimization * (1 - optimization_percentage)

    # Calculate the cost savings for RDS
    rds_cost_savings = rds_total_cost_without_optimization - rds_total_cost_with_optimization

    # Data visualization for RDS cost comparison
    rds_labels = ['Total Cost Without Optimization (RDS)', 'Total Cost With Optimization (RDS)']
    rds_values = [rds_total_cost_without_optimization, rds_total_cost_with_optimization]

    plt.figure(figsize=(8, 6))
    plt.bar(rds_labels, rds_values, color=['blue', 'green'])
    plt.ylabel('Cost ($)')
    plt.title('RDS Cost Comparison')

    # Save the RDS plot to a BytesIO object and encode it to base64
    rds_image = BytesIO()
    plt.savefig(rds_image, format='png')
    rds_image.seek(0)
    rds_plot_url = base64.b64encode(rds_image.getvalue()).decode()

def perform_s3_calculations(s3_cost_per_gb_month, s3_data_size_gb):
    global s3_plot_url, s3_total_cost_without_optimization, s3_total_cost_with_optimization, s3_cost_savings

    # Calculate the total cost for S3 without optimization
    s3_total_cost_without_optimization = calculate_s3_cost(
        s3_cost_per_gb_month, s3_data_size_gb
    )

    # Calculate the total cost for S3 with optimization (assume a 10% cost reduction)
    optimization_percentage = 0.10  # Adjust this percentage based on expected optimization results
    s3_total_cost_with_optimization = s3_total_cost_without_optimization * (1 - optimization_percentage)

    # Calculate the cost savings for S3
    s3_cost_savings = s3_total_cost_without_optimization - s3_total_cost_with_optimization

    # Data visualization for S3 cost comparison
    s3_labels = ['Total Cost Without Optimization (S3)', 'Total Cost With Optimization (S3)']
    s3_values = [s3_total_cost_without_optimization, s3_total_cost_with_optimization]

    plt.figure(figsize=(8, 6))
    plt.bar(s3_labels, s3_values, color=['blue', 'green'])
    plt.ylabel('Cost ($)')
    plt.title('S3 Cost Comparison')

    # Save the S3 plot to a BytesIO object and encode it to base64
    s3_image = BytesIO()
    plt.savefig(s3_image, format='png')
    s3_image.seek(0)
    s3_plot_url = base64.b64encode(s3_image.getvalue()).decode()


if __name__ == "__main__":
    app.run(debug=True)