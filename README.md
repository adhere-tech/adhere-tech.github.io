About AdHere
==
AdHere is a systematic measurement framework for assessing websites’ compliance with 
Better Ads Standards. We have deployed AdHere across Alexa Top 1 Million websites and conducted an over four-month study 
to understand the violating ads in the wild and the evolution of those ads in response to the Standards.

Dataset
--
[Detailed explanations about dataset files](Data/DataInstruction.md).

A Glance at Results
--
### RQ-A  Prevalence
![Unable to display figure1. Check browser settings.](figs/data_8.png)

The figure shows how websites changing its status during the research period. "FAILING" means Google claims the website
containing annoying ads, "PASSING" means Google thinks the website containing no violating ads.
We can find that the curve of FAILING websites is slowly falling down. The trend of PASSING websites
has a flat curve.

### RQ-B  Ad Networks
![Unable to display table1. Check browser settings.](figs/table_3.png)

The above table shows that in some violating ads our program automatically identified, the frequency of each ad network appears
and how data distributed on three violating ad types and on two platforms.  
We can find that 
ExoClick, Google Ads, and JUICYADS are the most prominent ad networks presented tendency to deliver violating ads. 
Developers may try not to use these adult ad networks if applicable, 
to reduce the possibility introducing violating ads to the website. 
Developers should also carefully configure the ads when using Google Ads 
to avoid introducing violating ads by mistake. 

### RQ-C  Fix Practices - A Modification Fix Example

The fix example happens on the mobile-version home page of "getsongbpm.com", a website telling the 
bpm (beats per minute) of songs. The following figure shows the fix process.

![Unable to display figure2. Check browser settings.](figs/merged.png)

The above figure shows two screenshots. Screenshot (left) displays the web page before the fix, screenshot (right) shows 
the web page after the fix. The red square shows an Pop-up ad blocking interactions with any 
other elements on the web page, which is considered violating based on Better Ads Standards. 
The green square shows a normal ad replacing the violating Pop-up ad.

[You can find two versions (before and after the fix) of the complete source code here](https://github.com/adhere-tech/adhere-tech.github.io/tree/master/Data/fix_example).  
Code snippet of Pop-up ad (line numbers are positions in the source file, the same below):
```
   1    <html><body>...
5694    <!--ADHERE: pop-up ad starts. You can find this comment at line 5694 in file-->
5695    <div id="aic-root-container-250">...
5697        <iframe id="aic-frame-66">...
5700            <html><body><div><div>...
5930                <div id="ad_unit">
5931                    <div class="GoogleActiveViewElement">...
5938                        <div class="GoogleCreativeContainerClass">
                                <!--ADHERE: ad image. You can find this comment at line 5938 in file-->
5938                            <a target="_blank" src="https://s0.2mdn.net/simgad/..." alt="Advertisement"></a>
                            </div>
                        </div>
                    </div>
                </div></div></body></html>
            </iframe>
        </div>...
6322    <!--ADHERE: pop-up ad ends. You can find this comment at line 6322 in file-->
        </body></html>
```

Code snippet of normal ad:
```
   1    <html><body>...
4712    <section id="content">...
4752        <div class="container"><div>...
4754            <!--ADHERE: normal ad starts. You can find this comment at line 4754 in file-->
4755            <div class="leadboard addmt"><div>...
4772                <div id="google_ads_iframe_/53015287/getsongbpm.com_m_300x250_1_0__container__">...
4774                    <iframe id="google_ads_iframe_/53015287/getsongbpm.com_m_300x250_1_0">...
4780                        <html><body><div>...
5587                            <div id="google_image_div">...
5588                                <a href="https://www.googleadservices.com/pagead/..." target="_blank">
5590                                    <amp-img>...
                                            <!--ADHERE: ad image hosted on Google Ads. You can find this comment at line 5594 in file-->
5594                                        <img src="https://tpc.googlesyndication.com/daca_images/simgad/...">
                                        </amp-img>
                                    </a>
                                </div>
                            </div></body></html>
                        </iframe>
                    </div>
                </div></div>...
6035            <!--ADHERE: normal ad ends. You can find this comment at line 6035 in file-->
            </div></div>
        </section></body></html>
```
