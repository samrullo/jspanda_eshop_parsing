# To find elements
Example

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up the driver (example uses Chrome)
driver = webdriver.Chrome()

# Open the webpage
driver.get("https://example.com")

# Find the table by class name (example: "my-table-class")
table = driver.find_element(By.CLASS_NAME, "my-table-class")

# If there are multiple tables with the same class
# tables = driver.find_elements(By.CLASS_NAME, "my-table-class")

# Print table HTML
print(table.get_attribute("outerHTML"))

# Always close the driver when done
driver.quit()
```

# To parse table data

To parse table data use below code

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://example.com")

# Step 1: Find the table element
table = driver.find_element(By.CLASS_NAME, "my-table-class")

# Step 2: Get all rows in the table
rows = table.find_elements(By.TAG_NAME, "tr")

# Step 3: Loop through rows and extract cell data
for row in rows:
    # Get all cells (td or th) in the row
    cells = row.find_elements(By.TAG_NAME, "td")
    if not cells:  # If no <td>, try <th> (for headers)
        cells = row.find_elements(By.TAG_NAME, "th")
    
    # Extract and print cell text
    cell_texts = [cell.text.strip() for cell in cells]
    print(cell_texts)

driver.quit()
```