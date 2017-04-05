# Amazon_reviews_agregator
Parse the Amazon products under a provided BrowseNodeId and extract the reviews text and 5star ranking 

3 OS environment variables API_KEY_AMAZON, API_SECRET_AMAZON, API_ASSOCIATE_AMAZON must be defined with respectively your Amazon Key, Amazon Secret and Amazon Associate Id.

Example of usage: Amazon_Reviews.py 565108

The scripts require a BrowseNode ID (here I put 565108) value that every products below will be parsed.
To identify this value, you can query a product of that category and check the response.

An optional export_ASIN parameter allows to dump the ASIN id related to the review.

Example: Amazon_Reviews.py 565108 export_SKU
