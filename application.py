from flask import Flask, render_template, request, jsonify
import requests
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import csv

logging.basicConfig(filename= "scraper.log", level= logging.INFO)

application = Flask(__name__)

app = application

@app.route("/", methods= ["GET"])
@cross_origin()
def search():
    return render_template("index.html")

@app.route("/review", methods= ["POST", "GET"])
@cross_origin()
def review():
    if request.method == "POST":
        try:
            searchString = request.form["content"].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            url_client = uReq(flipkart_url)
            flipkart_page = url_client.read()
            flipkart_html = bs(flipkart_page, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0: 3]
            bigbox = bigboxes[0]
            product_link = "https://www.flipkart.com" + bigbox.div.div.a["href"]
            product = requests.get(product_link)
            product.encoding = "utf-8"
            product_html = bs(product.text, "html.parser")
            logging.info(product_html)
            commentboxes = product_html.find_all("div", {"class": "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w+")
            headers = "product, customer name, rating, heading, comment \n"
            fw.write(headers)
            reviews = []


            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all("p", {"class":"_2sc7ZR _2V5EHH"})[0].text
                    
                
                except:
                    name = "no name"
                    logging.info(name)
                try:
                    rating = commentbox.div.div.div.div.text
                
                except:
                    rating = "no rating"
                    logging.info(rating)

                try: 
                    commenthead = commentbox.div.div.div.p.text
                    
                
                except:
                    commenthead = "no comment head"
                    logging.info(commenthead)
                
                try: 
                    comment_tag = commentbox.find_all("div", {"class": ""})
                    cust_comment = comment_tag[0].text

                except Exception as e:
                    logging.info("Exception while creating dictionary", e)

                mydict = {"product": searchString, "Name": name, "Rating": rating, "CommentHead": commenthead, "Comment": cust_comment}
                    
                reviews.append(mydict)
                logging.info(f" {reviews}")

            return render_template("result.html",  reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info("the exception is: ", e)
            return "something is wrong"
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(host= "localhost", port = 5400)