# AdHere

AdHere is an automated framework that assesses compliance with the Better Ads Standards and
helps website developers to detect, pinpoint, and fix the violations.
AdHere can precisely pinpoint ads on the fly and identify participating ad networks. 
It can also provide fix suggestions for developers to either change
ad attributes to comply with the Better Ads Standards or remove
the problematic ads from the page.

This repository contains the source code of AdHere, 
the script used for the preliminary study, and the dataset.
The Preliminary Study Toolset is used to get the compliance status from Google Ad Experience Report.

## Dependencies
- Python 3 (recommended >= 3.7)  
- Python3 libraries: Selenium, lxml, wmi, pywin32, requests
- Google Chrome (recommended >= 79) 
- [ChromeDriver](https://chromedriver.chromium.org/): Version corresponding to Chrome version and OS

## Setup Instructions

Before deployment, please first download 
the source code [here](https://github.com/adhere-tech/adhere-tech.github.io/tree/master/SourceCode).
#### AdHere
1. Install Python 3.
2. Install Selenium with `pip install selenium`, lxml with `pip install lxml`, 
wmi with `pip install wmi`, pywin32 with `pip install pywin32`, and requests with `pip install requests`.
3. Based on the OS and Chrome version, 
download the corresponding version of Chromedriver [here](https://chromedriver.chromium.org/). 
Unzip the downloaded file and put `chromedriver.exe` in the same folder as `AdHere.py`.
4. Fill Google Chrome's user profile directory after `USRPROFILE = ` in `AdHere.py`.
5. Run `python AdHere.py domain_url` in the command line to run AdHere on the given URL. 
Leaving `domain_url` blank will perform a self-inspection on google.com.
It will scan the website with the headless (no GUI) Google Chrome. After finishing the scan,
AdHere will generate `violations.txt` in the same folder as `AdHere.py`. 
The text file contains violations (i.e., the id, violation type, and XPath) and their fix suggestions.
    
#### Preliminary Study Toolset
1. Install all [dependencies](adhere-tech.github.io#dependencies).
2. Create at least one project using Google Ad Experience Report API in Google Developer Console. 
3. Apply for the API key for each project. Fill them in `API_KEY_LIST` in `google.py`. 
Adjust `THREAD_COUNT` based on the comments in `google.py`.
4. Run `python google.py` in the terminal to get Google Ad Experience Report's result of Alexa top 1 million websites.
Make sure the network connection is stable.
5. In the generated files,`[R]Alexa_done [XX_XX].csv` is the raw file to be stored in the database. 
It records the compliance status of the 1 million websites.


## Dataset

Due to the large volume of data, this section only lists 
a small portion of the data generated from our preliminary study and the evaluation of AdHere.
Complete dataset (1.1 GB tar.gz file) can be found [here](https://drive.google.com/file/d/1lUGUj2bLEhMzKzJ-5goCx7bAqc7tN3Zc/view?usp=sharing).

#### Alexa-result_Sep_10_2020.csv
This file contains Google Ad Experience Report’s result samples
of the Alexa Top 1 Million Websites collected on September 10th, 2020.
<iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSGx9nPZIDXRfVwhFt4rTM_bVbWagirlg6wVuvP2bB79_0ZndvWe_ZTi_BVyWEacVhPUchVuTF4R2yr/pubhtml?gid=2041000367&amp;single=true&amp;widget=true&amp;headers=false" loading allowfullscreen width="100%" height="300"></iframe>

#### fix_list.csv
This file contains the raw data of violating ad fix time.
<iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSGx9nPZIDXRfVwhFt4rTM_bVbWagirlg6wVuvP2bB79_0ZndvWe_ZTi_BVyWEacVhPUchVuTF4R2yr/pubhtml?gid=1068233299&amp;single=true&amp;widget=true&amp;headers=false" loading allowfullscreen width="100%" height="300"></iframe>

#### adhere_partial.csv
This file contains violating ad samples found by AdHere.
<iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSGx9nPZIDXRfVwhFt4rTM_bVbWagirlg6wVuvP2bB79_0ZndvWe_ZTi_BVyWEacVhPUchVuTF4R2yr/pubhtml?gid=911669432&amp;single=true&amp;widget=true&amp;headers=false" loading allowfullscreen width="100%" height="300"></iframe>

#### top_1m.csv
This is the samples of Alexa Top 1 Million Websites list.
<iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSGx9nPZIDXRfVwhFt4rTM_bVbWagirlg6wVuvP2bB79_0ZndvWe_ZTi_BVyWEacVhPUchVuTF4R2yr/pubhtml?gid=2070170508&amp;single=true&amp;widget=true&amp;headers=false" loading allowfullscreen width="100%" height="300"></iframe>

#### fix_example
This file contains the source code of the fix example on "getsongbpm.com". 
Details about this example can be found [in Finding 3](#finding-3-fix-with-attribute-modification---a-case-study).


## Findings

#### Finding 1. Website Coverage
![Unable to display figure1. Check browser settings.](figs/data_8.png)

Among the websites being reviewed by Google, the average
number of mobile websites failed daily is 884 while the desktop
version is 690. Moreover, the average numbers of websites passed
daily are 53,353 for mobile and 61,025 for desktop. The above figure shows the
number of sites with the PASSING status and FAILING status from
April 13, 2019 to August 18, 2019.
In general, among those that have been reviewed, we observed a
consistent trend that mobile websites contain more violating
ads than the desktop version. However, the numbers of violating
sites for both platforms are declining.

#### Finding 2. Ad Networks
![Unable to display table1. Check browser settings.](figs/table_4.png)

The above table shows ad network statistics from 13,438 ads collected from
Fail websites marked by AdHere on August 19th, 2020. 
As can be seen, ExoClick, Google Ads, and JUICYADS were the
most prominent ad networks presented the tendency to deliver violating
ads. Note that these top networks delivering violating
ads are not necessarily popular networks. According to the statistics
provided by W3Techs, 71.4% (15 out of 21) of these networks
are unranked and have market share much less than 0.1%.

#### Finding 3. Fix with Attribute Modification - A Case Study

The fix example happens on the mobile website "getsongbpm.com", 
a website telling the bpm (beats per minute) of songs. 
The following figure shows how a violating ad was fixed.
The screenshot on the left shows the web page before the fix 
and the screenshot on the right shows the page after the fix. 
The red square on the left highlights a Pop-up Ad that blocks interactions with other elements. 
Based on the Better Ads Standards, this Pop-up Ad is violating the standards. 
A normal ad was used to fix the violation. 
The green square on the right shows that the Pop-up was replaced by a normal ad. 

![Unable to display figure2. Check browser settings.](figs/merged.png)

The code snippets of the page before and after the fix are shown below.

Code snippet of Pop-up Ad (line numbers are positions in the source file):
```html
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

Code snippet of the normal ad:
```html
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


## Related

This is the extended Related Work section by including discussions on more related works 
and including the papers suggested by the reviewers.


### Online Ad Experiences. 
Much research effort has been made to study the impact of advertisements on website performance and quality of web experience [7,8,11–13,25,27]. However, these works do not focus on intrusive ads and the compliance with the Better Ads Standards. Prior works have proposed systems for delivering online advertisements to users. [3] presents a platform where users can configure their own adaptive profiles with personal preferences. Ads are tailored for the individual to create a more enjoyable user experience. [8,25] conducted studies that measure impact of advertisements and other contributing factors on the performance of webpages. A study [12] of 21 Android Apps concluded that in-app advertisements depletes significantly more computational resources,network bandwidth, and energy. A subsequent evaluation [13] identified the most prominent ad-related complaints from user reviews. Adjust [27] offers web developers the ability to impose resource constraints on third-party ad events to enhance user experience. [7] analyzed existing state of the art metrics for assessing web users quality of experience, and provide two new metrics to enhanced insight on the topic. [11] examined the relationship between ad exposure and the likelihood of a user remembering it. [18] designed a novel automated approach for repairing mobile friendly problems in web pages. [6] investigated explanations for the effectiveness of one of various video ad-choice formats, advertisement choice, and potential variations of this format.

### Ad Blockers.

Ad blockers (such as AdBlock Plus, uBlock Origin,and AdGuard [1,14,19]) are tools designed to conceal advertisements on a web page from the user. Ads are blocked by either blocking known ad hosting domains or detecting DOM elements in the HTML that match ID patterns and are subsequently made invisible [29]. There are two dominant perspectives on the usage of ad blockers. While one perspective maintains that advertisements are intrusive [22] and users should possess complete autonomy over what ad is considered acceptable and privacy-preserving [10,14,15]. Furthermore, ad blockers are capable of limiting user tracking and preserving privacy [10]. Others believe that online advertising is a necessary revenue stream for free websites. Several methods de-signed to circumvent ad blockers or whitelist acceptable ads have been proposed [2,4,26,29]. For example, WebRanz [29] uses randomization that continuously mutates HTML elements and their attributes, rendering ad blockers unable to recognize ad patterns without altering the appearance of the web page. This renders adblockers useless, as they are unable to recognize advertisement patterns. A common solution [4] for websites detects if a user has an ad blocker installed and requires them to either turn it off or subscribe to a service. [5] analyses the experiments to create Better Ads Standards and explains that highly annoying ads should not only be banned for practical reasons but for overpassing ethical limits. Beyond the Better Ads Standards, AdBlock Plus announced in 2011 their Acceptable Ads program, where developers can pay to have their “acceptable” ads (as set forth by the Acceptable Ads Committee [2]) whitelisted from the extension [20]. A comprehensive study [26] showed that the number of participating domains has drastically grown since the program’s inception, most of which do not disclose their relationship to the user. 

### Privacy and Security Implications. 

Our work is also related to privacy and security implications of online advertising [16,21,23,28]. AdJail [24] provides an innovative framework that enables web developers to mitigate potentially harmful ad practices that jeopardize user confidentiality and integrity. AdSentry [9] protects users from untrusted JavaScript-based ads by isolating their expo-sure to the main page via customizable access control policies. [16] demonstrates how JavaMOP, a runtime verification system, can be leveraged to define and monitor Java security policies. Malvertising is the act of delivering malware to the victim through advertisements [28], with or without any interaction from the user [23]. Mad-Tracer [17] detects malvertising through dynamic rule generation. [30] conducted a large-scale study of the origins of malvertising and showed that websites without explicit contracts with advertisers are prone to delivering malicious ads. The authors of [21] developed a classifier-based framework for identifying malicious advertisements.

REFERENCES

[1] AdGuard. 2019. AdGuard: The world’s most advanced ad blocker! https://adguard.com/.

[2] Acceptable Ads. 2019. Acceptable Ads Standards. https://acceptableads.com/en/.

[3] Florian Alt, Moritz Balz, Stefanie Kristes, Alireza Sahami Shirazi, Julian Mennenöh, Albrecht Schmidt, Hendrik Schröder, and Michael Goedicke. 2009. Adaptive user profiles in pervasive advertising environments. In European Conferenceon Ambient Intelligence. Springer, 276–286.

[4] Antiblock. 2019. Anti Adblock Script. https://antiblock.org/.

[5] Daniel Belanche. 2019. Ethical limits to the intrusiveness of online advertising formats: A critical review of Better Ads Standards. Journal of marketingcommunications25, 7 (2019), 685–701.

[6] Steven Bellman, Robert F Potter, Jennifer A Robinson, and Duane Varan. 2020. The effectiveness of various video ad-choice formats. Journal of Marketing Communications (2020), 1–20.

[7] Enrico Bocchi, Luca De Cicco, and Dario Rossi. 2016. Measuring the quality of experience of web users. ACM SIGCOMM Computer Communication Review46, 4(2016), 8–13.

[8] Michael Butkiewicz, Harsha V Madhyastha, and Vyas Sekar. 2011. Understanding website complexity: measurements, metrics, and implications. In Proceedings of the 2011 ACM SIGCOMM conference on Internet measurement conference. ACM, 313–328.

[9] Xinshu Dong, Minh Tran, Zhenkai Liang, and Xuxian Jiang. 2011.  AdSentry: comprehensive and flexible confinement of JavaScript-based advertisements. In Proceedings of the 27th Annual Computer Security Applications Conference. ACM,297–306.

[10] Kiran Garimella, Orestis Kostakis, and Michael Mathioudakis. 2017. Ad-blocking: A study on performance, privacy and counter-measures. In Proceedings of the 2017 ACM on Web Science Conference. ACM, 259–262.

[11] Daniel G Goldstein, R Preston McAfee, and Siddharth Suri. 2011. The effects of exposure time on memory of display advertisements. In Proceedings of the 12th ACM conference on Electronic commerce. ACM, 49–58.

[12] Jiaping Gui, Stuart Mcilroy, Meiyappan Nagappan, and William GJ Halfond. 2015. Truth in advertising: The hidden cost of mobile ads for software developers. In Proceedings of the 37th International Conference on Software Engineering - Volume1. IEEE Press, 100–110.

[13] Jiaping Gui, Meiyappan Nagappan, and William GJ Halfond. 2017. What aspects of mobile ads do users care about? An empirical study of mobile in-app ad reviews. arXiv preprint arXiv: 1702.07681(2017).

[14] Raymond Hill. 2019. uBlock Origin.  https://github.com/gorhill/uBlock.

[15] Raymond Hill. 2019. uBlock Origin Manifesto. https://github.com/gorhill/uBlock/blob/master/MANIFESTO.md.

[16] Soha Hussein, Patrick Meredith, and Grigore Roşlu. 2012. Security-policy monitoring and enforcement with JavaMOP. In Proceedings of the 7th Workshop on Programming Languages and Analysis for Security. ACM, 3.

[17] Zhou Li, Kehuan Zhang, Yinglian Xie, Fang Yu, and XiaoFeng Wang. 2012. Knowing your enemy: understanding and detecting malicious web advertising. In Proceedings of the 2012 ACM conference on Computer and communications security. ACM, 674–686.

[18] Sonai Mahajan, Negarsadat Abolhassani, Phil McMinn, and William G. J. Halfond. 2018. Automated Repair of Mobile Friendly Problems in Web Pages. In Proceedings of the 40th International Conference on Software Engineering (Gothenburg, Sweden) (ICSE ’18). Association for Computing Machinery, New York, NY, USA, 140–150. https://doi.org/10.1145/3180155.3180262

[19] Adblock Plus. 2019. Adblock Plus. https://adblockplus.org/.

[20] AdBlock Plus. 2019.Allowing acceptable ads in Adblock Plus. https://adblockplus.org/acceptable-ads

[21] Prabaharan Poornachandran, N Balagopal, Soumajit Pal, Aravind Nair, Prem a U,and Manu R. Krishnan. 2017. Demalvertising: A Kernel Approach for Detecting Malwares in Advertising Networks. 215–224. https://doi.org/10.1007/978-981-10-2035-3_23

[22] Enric Pujol, Oliver Hohlfeld, and Anja Feldmann. 2015.  Annoyed users: Ads and ad-block usage in the wild. In Proceedings of the 2015 Internet Measurement Conference. ACM, 93–106.

[23] Dilan Samarasinghe. 2019. Malvertising. https://www.cisecurity.org/blog/malvertising/.

[24] Mike Ter Louw, Karthik Thotta Ganesh, and VN Venkatakrishnan. 2010. AdJail: Practical Enforcement of Confidentiality and Integrity Policies on Web Advertisements. In USENIX Security Symposium. 371–388.

[25] Martin Varela, Lea Skorin-Kapov, Toni Mäki, and Tobias Hoßfeld. 2015.  QoE in the Web: A dance of design and performance. In 2015 Seventh International Workshop on Quality of Multimedia Experience (QoMEX). IEEE, 1–7.

[26] Robert J Walls, Eric D Kilmer, Nathaniel Lageman, and Patrick D McDaniel.2015.  Measuring the impact and perception of acceptable advertisements. In Proceedings of the 2015 Internet Measurement Conference. ACM, 107–120.

[27] Weihang Wang, I Luk Kim, and Yunhui Zheng. 2019. Adjust: runtime mitigation of resource abusing third-party online ads. In Proceedings of the 41st International Conference on Software Engineering. IEEE Press, 1005–1015.

[28] Weihang Wang, Yonghwi Kwon, Yunhui Zheng, Yousra Aafer, I Kim, Wen-ChuanLee, Yingqi Liu, Weijie Meng, Xiangyu Zhang, Patrick Eugster, et al.2017. PAD: Programming third-party web advertisement censorship. In Proceedings of the32nd IEEE/ACM International Conference on Automated Software Engineering. IEEE Press, 240–251.

[29] Weihang Wang, Yunhui Zheng, Xinyu Xing, Yonghwi Kwon, Xiangyu Zhang, and Patrick Eugster. 2016. Webranz: web page randomization for better advertisement delivery and web-bot prevention. In Proceedings of the 2016 24th ACM SIGSOFT International Symposium on Foundations of Software Engineering. ACM, 205–216.

[30] Apostolis Zarras, Alexandros Kapravelos, Gianluca Stringhini, Thorsten Holz, Christopher Kruegel, and Giovanni Vigna. 2014.  The dark alleys of madison avenue: Understanding malicious advertisements. In Proceedings of the 2014 Conference on Internet Measurement Conference. ACM, 373–380.