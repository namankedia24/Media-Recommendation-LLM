!pip install -r requirements.txt

# For Colab, there were package conflicts when I tried
# installing the requirements, so running 
# the lines below helped me resolve them. 

# !pip uninstall tensorflow tensorflow-metadata -y
# !pip install -r requirements.txt

!python data_downloading.py
!python data_processing.py
!python vector_store_construction.py
!python system.py
