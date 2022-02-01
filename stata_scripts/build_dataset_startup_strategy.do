

/****
 **

	This code builds thev underlying analysis data for 
		Guzman, Jorge, and Aishen Li. 2020. Measuring Founding Strategy.
		
	It assumes the user has access to the csv files provided by Crunchbase 
	in their data sharing license. 
	
 **
 *****/


cd /Users/jag2367/Documents/GitHub/startup-website-performance/Statistics/Stata

global data_path /Users/jag2367/Documents/GitHub/startup-website-performance/Data/tfidf


/*** Prepare preqin deals data **/


if 0 { 
	


	/** 
		CRUNCHBASE
		Prepare Crunchbase Deals Data 
		**/
	clear
	dir $data_path/../Crunchbase/
	use $data_path/../Crunchbase/funding_rounds.dta , replace
	merge m:1 org_uuid using  $data_path/../Crunchbase/crunchbase_orgs.dta 
	keep if _merge == 3
	drop _merge
	gen investment_date = date(announced_on, "YMD")

	tomname name 
	save all_deals.crunchbase.dta , replace

	
	
	clear
	import delimited using $data_path/../Crunchbase/ipos.csv , varnames(1)
	keep if inlist(stock_exchange_symbol, "nasdaq","nyse","nysemkt")
	gen ipo_date = date(went_public_on ,"YMD")
	bysort org_uuid (ipo_date): gen first = _n == 1
	keep if first
	drop first

	drop name
	merge 1:m org_uuid using  all_deals.crunchbase.dta
	drop if _merge == 1
	gen ipo = _merge == 3
	drop _merge
	rename money_raised_usd  ipo_money_raised
	rename valuation_price_usd  ipo_valuation

	gen ipo_year = year(ipo_date)
	gen time_to_ipo = ipo_date - founding_date
	gen bad_ipo =  time_to_ipo < 180
	save all_deals.crunchbase.dta , replace


	clear
	import delimited using $data_path/../Crunchbase/acquisitions.csv , varnames(1) 

	rename acquiree_uuid org_uuid
	gen acquisition_date = date(acquired_on ,"YMD")
	bysort org_uuid (acquisition_date): gen first = _n == 1
	keep if first
	drop first
	merge 1:m org_uuid using  all_deals.crunchbase.dta
	drop if _merge == 1 
	drop if inlist(acquisition_type, "lbo", "merge")
	gen acquired = _merge == 3 & ipo_date == . 
	gen acquihire = inlist(acquisition_type, "acquihire","management_buyout")
	gen acq_merger = inlist(acquisition_type, "merge")
	drop _merge

	rename price_usd acq_price
	replace acq_price = . if ipo_date != .

	gen acq_date = date(acquired_on,"YMD")
	gen acq_year = year(acq_date)
	gen time_to_acq = acq_date - founding_date
	gen bad_acq = time_to_acq < 90
	
	save all_deals.crunchbase.dta , replace






	use all_deals.crunchbase.dta , replace
	
		
	drop if inlist(investment_type,"post_ipo_debit","post_ipo_equity","non_equity_assistance","initial_coin_offering","secondary_market","debt_financing")

	destring raised_amount_usd, force replace

	rename investment_type stage
	gen seed_angel = raised_amount_usd if stage == "seed" | stage == "angel"  | stage == "pre_seed"  | stage == "product_crowdfunding"
	gen angel = raised_amount_usd if  stage == "angel" 
	gen seed = raised_amount_usd if stage == "seed" 
	gen grant = raised_amount_usd if stage == "grant"
	
	format investment_date %d
	sort investment_date
	
	
	gen early_stage_amount = raised_amount_usd if stage == "seed" | stage == "angel"  | stage == "pre_seed"  | stage == "product_crowdfunding" | stage == "grant"
	
	
	gen series_inv = strpos(stage,"series") > 0
	bysort org_uuid (investment_date):gen num_series = sum(series_inv) if series_inv == 1
	
	/** series A rounds definition **/	
	gen is_series_a = 0
	replace is_series_a = 1 if stage == "series_a"  & num_series == 1  
	
	//Only up to 100 million investment to consider it series a, and only first series a investment
	gen series_a = raised_amount_usd if  is_series_a == 1  & inrange(raised_amount_usd,2.5*10^5, 1*10^8)
	
		
	gen series_b = raised_amount_usd if stage == "series_b"
	gen series_c = raised_amount_usd if stage == "series_c"
	gen series_d = raised_amount_usd if stage == "series_d"
	gen series_e = raised_amount_usd if stage == "series_e"

	gen incyear = founding_year
	gen years_to_deal = year(investment_date) - incyear


	drop if website == ""
	gen closed = status == "closed"

	gen dealyear = year(investment_date)
	gen early_stage_year = dealyear if stage == "seed" | stage == "angel"  | stage == "pre_seed"  | stage == "product_crowdfunding"

	
	
	collapse (max) acquired closed ipo bad_ipo bad_acq  acq_price is_series_a  (min) ipo_date early_stage_year ipo_year acq_year (sum)  count_series_a = is_series_a seed_angel seed angel series_*  grant early_stage_amount, by(org_uuid website incyear city state cbcat* name short_description)

	
	duplicates drop website , force

	
	save all_info.crunchbase.dta , replace




	use all_info.crunchbase.dta , replace

	save startup_info.dta , replace

	
	use startup_info.dta , replace
 list if strpos(lower(name),"magic leap")
}

	/***********************************************************/




	clear
	set more off
	gen year = .
	save analysis.pre.dta , replace


	forvalues year = 2003/2018 { 

		use $data_path/`year'.website_info.dta , replace
		capture drop index 
		duplicates drop website,  force
		save website_info.dta , replace

		clear 
		use $data_path/`year'.similarity_scores.dta
		

		rename website_name website
		merge m:1 website using website_info.dta
		keep if _merge == 3
		drop _merge

		keep if type == "startup"
		
		merge m:1 website using startup_info.dta 
		drop if _merge ==2
		drop _merge
		
		
		gen year = `year'
		
		append using analysis.pre.dta
		save analysis.pre.dta , replace
	}



clear
 use analysis.pre.dta , replace
 
//gen early_stage = grant + angel + seed 
gen early_stage = early_stage_amount


foreach v of varlist  early_stage seed angel seed_angel series_* grant  acq_price{ 
	gen log_`v' = log(`v'+1) 
}




gen ind = ""
capture replace ind = primaryindustry
replace ind = cbcat1 
tab year , gen(Y_)
encode city , gen(citycode)
encode state , gen(statecode)


gen growth = ipo== 1 | acquired == 1
replace grant = 0 if missing(grant)



foreach v of varlist seed angel grant series_a series_b series_c series_d ipo acquired  early_stage{ 
	gen gets_`v' = `v' >0 & `v' !=. 
	sum gets_`v'
}
replace grant = 0 if grant == .

save analysis.not_cleaned.dta, replace


	
	

use analysis.not_cleaned.dta, replace
 
//drop if bad_ipo == 1 
drop if  bad_acq == 1

sum website_len , detail
xtile wlbin = website_len , nq(20)

//drop if inlist(ind,"Commercial Real Estate","Finance")

replace ipo = 0 if ipo == .| ipo_year == .
replace acquired = 0 if acquired == . | acq_year == .
duplicates drop website, force
replace acquired =0 if ipo == 1 & ipo_year < acq_year 
replace ipo = 0 if  ipo_year < incyear 
replace ipo_year = . if  ipo == 0
replace acquired = 0 if  acq_year < incyear 
replace acq_year = . if  acquired == 0

capture drop bio 
capture drop finance 
capture drop early_stageTh
gen bio =  strpos(lower(ind),"biotech") | strpos(lower(ind),"biopharma")
gen finance = strpos(lower(ind),"finance") | strpos(lower(ind),"real estate") | strpos(lower(ind),"property development")
replace early_stage = 0 if early_stage == .
gen early_stageTh = early_stage/1000
replace log_early_stage = log(early_stage+1)




/** new stuff **/

tab year, gen(_Y)
gen log_early_stage2 = log(early_stage)

xtile wlq = website_len , nq(20)
tab wlq, gen(_wlq)
tab early_stage_year,  gen(_eY)

save analysis.dta , replace


use analysis.dta , replace
label variable log_early_stage "Log(Early Stage Financing)"
label variable gets_early_stage "Gets Early Stage Financing"
label variable early_stageTh "Early Stage Financing (Thousands $)"
label variable website_len "Website Text Length"
label variable growth "Equity Growth (IPO or Acquisition)"
label variable acquired "Acquisition"
label variable ipo "IPO"


label variable bio "Industry:Biotechnology"




/**** Key Strategy Definitions *****************/

gen nov_public_firm_5 = 1 - w2v_sim_public_firm_5 
gen nov_public_firm_1 = 1 - w2v_sim_public_firm_1 
gen nov_startup_5 = 1 - w2v_sim_startup_5 
gen nov_startup_1 = 1 - w2v_sim_startup_1 

label variable nov_public_firm_5 "Differentiation Score (5 Closest Public Firms)"
label variable nov_public_firm_1 "Differentiation Score (Closest Public Firm)"
label variable nov_startup_5 "Differentiation Score (5 Closest Cohort Startups)"
label variable nov_startup_1 "Differentiation Score (Closest Cohort Startups)"

sort nov_public_firm_5


gen x = log10(website_len) 
local xline = log10(150000)

sum x , detail
//drop if x  > `r(p99)'


replace city = "none" if city == ""

capture drop log_seed
gen log_seed = log(seed +1)

capture drop log_up_to_a
gen log_up_to_a  = log(series_a + early_stage + 1)
save analysis.dta , replace



use  analysis.dta , replace


//sum tfidf_nov_public_firm_5, detail
//drop if tfidf_nov_public_firm_5 < `r(p10)'

save analysis.dta , replace


use  analysis.dta , replace
capture drop hp_industry

save  analysis.dta , replace


use "$data_path/hp_industries.website_info.dta" , replace
duplicates drop website, force
keep website hp_industry 

merge 1:m website using analysis.dta
drop if _merge == 1
drop _merge 
drop if org_uuid == ""

save analysis.dta , replace


use  analysis.dta , replace
save analysis.allobs.dta , replace



use analysis.allobs.dta , replace

**drop if year > 2017

split name, limit(2)
rename name1 name_first_word
*drop if strpos(lower(text), lower(name_first_word)) == 0
drop if strpos(text,"Wayback Machine") == 1
drop if strpos(text,"domain") 
drop if inrange(strpos(lower(text),"not found"), 1, 5)
drop if strpos(lower(text),"apache")  
drop if strpos(lower(text),"unix") 


merge 1:1 org_uuid using "$data_path/closest_snapshots_list.dta"
drop if _merge == 2
gen timestamp_year = substr(closest_snapshot_time,1,4 )
destring timestamp_year , replace
gen timestamp_gap = timestamp_year-founding_year
tab timestamp_gap , missing





replace citycode = 0 if citycode == .
replace statecode = 0 if citycode == .
di _N


//local var w2v
local var abt


replace nov_public_firm_5 = 1 - `var'_sim_public_firm_5
replace nov_public_firm_1 = 1- `var'_sim_public_firm_1  
replace nov_startup_5 = 1- `var'_sim_startup_5  
replace nov_startup_1 = 1- `var'_sim_startup_1  


local add_median 0
if `add_median' == 1 & "`var'" == "w2v"{
	replace nov_public_firm_5 = 1 - `var'_sim_public_firm_5 + `var'_sim_public_median
	replace nov_public_firm_1 = 1- `var'_sim_public_firm_1  + `var'_sim_public_median
	replace nov_startup_5 = 1- `var'_sim_startup_5  + `var'_sim_startup_median
	replace nov_startup_1 = 1- `var'_sim_startup_1  +`var'_sim_startup_median
	
}

safedrop clean_nov

set scheme s1mono
sum nov_public_firm_5, detail

gen clean_nov = nov_public_firm_5 if nov_public_firm_5 > `r(p5)' & nov_public_firm_5 < `r(p95)'

twoway  (hist nov_public_firm_5, freq) 

graph export  "../../tex2/hist_nov_public_firm.png", as(png) width(800) height(400) replace



global winsorize 1
if $winsorize == 1 {

	sum nov_public_firm_5, detail
	drop if nov_public_firm_5 <= `r(p5)' | nov_public_firm_5 >= `r(p95)'
}


global remove_bottom_5pct 0
if $remove_bottom_5pct == 1 {
	sum nov_public_firm_5, detail
	drop if nov_public_firm_5 < `r(p5)'
}


drop if website_len > 100000
//binscatter website_len nov_public_firm_5


gen tfidf_public_firm_5 = 1- tfidf_sim_public_firm_5

gen tfidf_public_firm_1 = 1- tfidf_sim_public_firm_1  
gen tfidf_startup_5 = 1- tfidf_sim_startup_5  
gen tfidf_startup_1 = 1- tfidf_sim_startup_1  


//replace nov_public_firm_5 = 1 - w2v_sim_public_firm_5 + w2v_sim_public_median


save analysis.allobs.dta , replace



clear
use analysis.allobs.dta , replace


gen time_gap = 100 + timestamp_gap

keep if inrange(time_gap,98,102)
//keep if inrange(time_gap,98,102)


keep if is_valid_website == 1


drop if strpos(text,"Wayback")
drop if strpos(text,"DF-1.4 %���� 0 obj< ") == 1
drop if strpos(text,"This page uses frames, but your brow") == 1
drop if strpos(name,"Real Estate")  & ipo
drop if strpos(text,"U N D E R C O N S T R U C T I O N")
drop if strpos(text," We recommend you upgrade your browser to one of below free alternatives")
drop if strpos(name,"LP")
drop if strpos(text,"enable JavaScript")
drop if inrange(strpos(text,"construction"),1, 100)
drop if strpos(text,"Page cannot be Please contact your service provider for more")
drop if strpos(text,".:: This Website For Sale ::. ")

drop if inrange(strpos(text,"Untitled Document Coming"),1, 100)
drop if inrange(strpos(text,"Adobe Flash"),1, 100) & website_len < 100
drop if strpos(text,"This site requires JavaScript ") == 1
drop if inrange(strpos(text,"Database Error"),1, 100)
drop if inrange(strpos(text,"Ubuntu"),1, 100)

//drop if inrange(strpos(lower(text),"coming soon"),1, 100)
//drop if inrange(strpos(text,"A WordPress Site"),1, 100)
drop if inrange(strpos(text,"Welcome to IIS"),1, 100)

drop if inrange(strpos(text,"A web page that points a browser to a different page "),1, 100)
 
drop if inrange(strpos(text,"registered users only"),1, 100)

drop if website == "www.luxera-led.com"
drop if inrange(strpos(text,"stealth mode"),1, 100)
 
 drop if strpos(lower(text),"coming soon") & text_len < 200


//drop if strpos(name,"Parametric Sound")
gen text_words = wordcount(text)



//Get rid of financial categories and financial IPOs / REIT / SPAC
drop if inlist(cbcat1,"Real Estate", "Property Development","Credit")
drop if strpos(text,"REIT")
drop if strpos(lower(text),"investment trust")


save analysis.dta , replace



clear
use analysis.dta

safedrop high_value_acq
gen high_value_acq = acquired == 1 & acq_price != . & acq_price > 10*10^7
label variable high_value_acq "High Value Acquisition (100M or more)"



egen year_ind = group(hp_ind year)

gen time_to_exit = .
replace time_to_exit = acq_year - year if acquired == 1
replace time_to_exit = ipo_year - year if ipo == 1

gen early_acquisition = time_to_exit <= 4 & acquired == 1
gen late_acquisition = time_to_exit > 4 & acquired == 1

drop if text_words < 10
drop if text_len < 100


save analysis.dta , replace



	






use analysis.dta , replace

