---
layout: post
title: "Iowa Housing: Continued Cleaning"
date: 2021-07-06
tags: [python, data exploration, data cleaning, feature engineering, machine learning, iowa housing]
---

Welcome back! In my last post about the Iowa Housing dataset, I covered the process of filling categorical and numerical `NA`s to keep as much data as possible. Somewhat naively, I assumed we\'d be ready for modelling; in reality, there is still a lot of work to be done.

To start with, I found more information about the dataset itself, and how others have approached this analysis task though the following links:

* [Ames, Iowa: Alternative to the Boston Housing Data as an End of Semester Regression Project \| Dean De Cock, Truman State University \| Journal of Statistics Education](http://jse.amstat.org/v19n3/decock.pdf)
* [Ames, Iowa Real Estate Analysis \| Mark Carthon](https://nycdatascience.com/blog/r/ames-iowa-real-estate-analysis/)
* [Prediction Model of Ames Real Estate Prices \| Authors not listed](https://rstudio-pubs-static.s3.amazonaws.com/337439_24918eaefe724411be93e41ede48b256.html)

The most important discovery was the [the full, unaltered dataset](http://jse.amstat.org/v19n3/decock.pdf). When I started this project, the data provided by the Kaggle competition was incomplete. The target variable `SalePrice` has already been removed from the `test_set`, and some features in the `train_set` had missing values. Now, thanks to Dean De Cock's article about the dataset, all of the data is available, including `SalePrice` for each sample.

In my last post about this dataset, I had to use 3 datasets when cleaning: `train_data`, `test_data`, and `merge_data`. Each cleaning step had to iterate over these three datasets, and treat them separately. Now, I will use `fulldatadf` to refer to all training examples, and will divide `fulldatadf` into training and testing subsets during modelling.

While looking at how others approached this analysis task, I made a list of important approaches others took that I missed:

#### Statistical approaches ####

* Filtering outliers using either graphical approach or IQR approach
* Recategorizing incorrectly labled numerical features as categorical features
* Mapping ordinal (ordered) categorical features to integer values (features that measure condition, such as `Functional` and `OverallCond`)
* Merging levels within categories with few instances into those with more and discarding features with too few instances

#### Domain knowledge approaches ####

* Using map data to determine distances to places of interest in Ames (Iowa State University, Airport, Downtown)
* Using `YearBuilt` and `Neighborhood` as filters to view their relationship to `SalePrice`
* Knowing a lot\'s `LotFrontage` can be `0` linear feet, and a value of `NA` does not mean we need to interpolate a value

As I walk through cleaning the dataset\'s features, it may be helpful to have [the dataset's documentation](http://jse.amstat.org/v19n3/decock/DataDocumentation.txt) open to check definitions and values. 

___

### Filtering Outliers ###

There are some outliers in important features `LotArea` and `GrLivArea`. First, I wanted to filter the data the <a href="https://www.statisticshowto.com/statistics-basics/find-outliers/">1.5 x Interquartile Range Rule</a>. Before filtering, there were 2930 samples; after filtering, this method left 2745 samples. Losing 185 samples, or 6.3% of our dataset is not trivial. The IQR filters approximately marked the following as outliers: `GrLivArea >= 2750` and `LotArea >= 24000`.

I then made another filter, based only on the graphs I had seen, with these marked as outliers: `GrLivArea >= 4000` and `LotArea >= 80000`. Below are the two features mapped against `SalePrice`, where non-outliers are marked in green, IQR determined outliers are marked in orange, and outliers determined by my graphical filter are marked with a star.

<p align=center>
<img src="/assets/images/CheckingforOutliersScatterPlot.svg" width = '95%'>
</p>

I generated the same graphs, using the logarithm of the features to see the distribution without the clumping around the origin in the second graph:

<p align=center>
<img src="/assets/images/CheckingforLogOutliersScatterPlot.svg"  width = '95%'>
</p>

These graphs helped me make the decision not to use the IQR filtering rule because it removes too many data points. The only points I feel confident removing based on `GrLivArea` are the three points in the lower right corner of the `GrLivArea` graph, as the other two marked by my filter still appear to follow the trend. The other points I feel confident removing based on `LotArea` are the four on the right side of the `LotArea` graph, since these lot sizes are far larger than any other lot seen in our dataset.

{% highlight python %}
grlivareafilter = fulldatadf['GrLivArea'] >= 4000
salepricefilter = fulldatadf['SalePrice'] <= 200000
lotareafilter   = fulldatadf['LotArea']   >= 80000

fulldatadf = fulldatadf[~((grlivareafilter & salepricefilter) | lotareafilter)]
{% endhighlight %}

___

### Improperly encoded features ###

These are 3 features that are supposed to be nominal but have been encoded using integers: `PID`, `MoSold`, and `MSSubClass`. Leaving these as numerical adds a context of weight to each feature that should not be present.

As well, when I later use `PID` to get address data out of a database, it needs a leading `0` in the string.

{% highlight python %}
fulldatadf['MoSold'] = fulldatadf['MoSold'].map(str)
fulldatadf['MSSubClass'] = fulldatadf['MSSubClass'].map(str)
fulldatadf['PID'] = '0' + fulldatadf['PID'].map(str)
{% endhighlight %}

Note that I will not be including `PID` in the model, but will be using it to pull address data from <a href='http://www.cityofames.org/assessor/'>the Ames site</a> (a post in and of itself, for a later date).

___

### Ordinal features ###

Of the 82 features, 46 are considered categorical - 23 ordinal, 23 nominal. In this section, I will recategorize some features, and map ordinal features to discrete numerics.

#### Remapping ordinal features to integer scale ####
`LotShape`, `Utilities`, `LandSlope`, `OverallQual`, `OverallCond`, `ExterQual`, `ExterCond`, `BsmtQual`, `BsmtCond`, `BsmtExposure`, `BsmtFinType1`, `BsmtFinType2`, `HeatingQC`, `Electrical`, `KitchenQual`, `Functional`, `FireplaceQu`, `GarageFinish`, `GarageQual`, `GarageCond`, `PavedDrive`, `PoolQC`, and `Fence` all have some implicit ordering associated.

This step takes advantage of the ordered quality of these features, and maps it to a linear scale. Defining a map, then applying said map for 20+ variables is very repetitive, so the full script is available [here](https://github.com) on my github.

As a short example, here is the process for `Functional`:

{% highlight python %}
# convert Functional to numerical
functional_map = {
        'Sal'  : 1,
        'Sev'  : 2,
        'Maj2' : 3,
        'Maj1' : 4,
        'Mod'  : 5,
        'Min2' : 6,
        'Min1' : 7,
        'Typ'  : 8
}
remap(fulldatadf,
             'Functional',
             functional_map)
{% endhighlight %}

___

### Nominal features ###
These are all categorical features that have no implicit ordering, so we will try to either merge low cardinality levels into a broader bin, or create new features using the levels within a feature. 

`PID`, `MSSubClass`, `MSZoning`, `Street`, `Alley`, `LandContour`, `LotConfig`, `Neighborhood`, `Condition1`, `Condition2`, `BldgType`, `HouseStyle`, `RoofStyle`, `RoofMatl`, `Exterior1`, `Exterior2`, `MasVnrType`, `Foundation`, `Heating`, `CentralAir`, `GarageType`, `MiscFeature`, `SaleType`, `SaleCondition`

#### MSSubClass ####
By the documentation, `MSSubClass` is a combination of 3 features: `HouseStyle`, `BldgType` and `YearBuilt`. In my opinion, the only important aspect of this feature is determining whether a home is part of a PUD (Planned Unit Development), as all other information is available in another feature. Below are the levels for `MSSubClass` with PUD in description, and the levels for the equivalent non-PUD home.

<table border="1" class="dataframe">
  <thead>
	<tr style="text-align: right">
   	  <th class="text">Non-PUD Code</th>
	  <th class="text">Description</th>
	  <th class="text">PUD Code</th>
	  <th class="text">Description</th>
	</tr>
  </thead>
  <tbody>
	<tr>
 	  <td data-title="Non-PUD Code" class="text">120</td>
	  <td data-title="Description" class="text">1 Story, 1946 and newer</td>
	  <td data-title="PUD Code" class="text">120</td>
	  <td data-title='Description' class='text'>1 Story PUD, 1946 and newer</td>
	</tr>
	<tr>
 	  <td data-title="Non-PUD Code" class="text">045, 050</td>
	  <td data-title="Description" class="text">1 1/2 Story, all ages</td>
	  <td data-title="PUD Code" class="text">150</td>
	  <td data-title='Description' class='text'>1 1/2 Story PUD, all ages</td>
	</tr>
	<tr>
 	  <td data-title="Non-PUD Code" class="text">060</td>
	  <td data-title="Description" class="text">2 Story, 1946 and newer</td>
	  <td data-title="PUD Code" class="text">160</td>
	  <td data-title='Description' class='text'>2 Story PUD, 1946 and newer</td>
	</tr>
	<tr>
 	  <td data-title="Non-PUD Code" class="text">080, 085</td>
	  <td data-title="Description" class="text">Split, multilevel, or split foyer</td>
	  <td data-title="PUD Code" class="text">180</td>
	  <td data-title='Description' class='text'>Multilevel PUD</td>
	</tr>
  </tbody>
</table>

<p align=center>
<img src="/assets/images/PUDMSSubclassSalePriceBox.svg" alt="Boxplot showing relation between Sale Price and MSSubClass" width = '90%'>
<img src="/assets/images/PUDMSSubclassSalePriceBar.svg" alt="Boxplot showing relation between Sale Price and MSSubClass" width = '90%'>
<br><sub>Note different scales for y-axis `SalePrice`</sub>
</p>

These graphs tell me that although PUD homes make up a smaller subset of the data and have less outliers, there are differences in mean price when sorted by PUD and non-PUD homes. From this, I will create a new binary column based on `MSSubClass` which will contain whether the home is part of a PUD or not and drop `MSSubClass`, as the remaining data can be found in `HouseStyle`, `BldgType` and `YearBuilt`.

{% highlight python %}
fulldatadf['isPUD'] = fulldatadf['MSSubClass'].apply(
    lambda x: 1 if x in PUD_list else 0)
{% endhighlight %}

#### MSZoning ####
This feature identifies the general zoning classification of the sale; since the goal is to predict a home\'s `SalePrice` for a potential homeowner, I will not include properties whose zoning is in `A` (Agriculture), `C` (Commerical), or `I` (Industrial) in the model, under the assumption that a potential homeowner will not be purchasing these kinds of property (this excludes 29 properties in total).

{% highlight python %}
# pre filtering
fulldatadf['MSZoning'].value_counts()
RL         2266
RM          462
FV          139
RH           27
C (all)      25
A (agr)       2
I (all)       2


# filter out commercial, industrial, and agricultural properties
MSZoning_cols = ['RL', 'RM', 'FV', 'RH']
MSZoning_mask = fulldatadf['MSZoning'].isin(MSZoning_cols)
fulldatadf = fulldatadf[MSZoning_mask]
{% endhighlight %}


#### Condition1 + Condition2 ####

There are 9 conditions detailed here, including adjacency to arterial street (high capacity urban roads), adjacency to feeder street (a secondary road used to bring traffic to a major road), located within 200' of a railroad, adjacency to a railroad, and adjacency to or located near a positive off-site feature, like a park or greenbelt. The proximity to railroads usually means higher frequency of loud noises, and possible traffic delays, while proximity to larger roads can mean faster commute times, or higher freqency of loud noises. These features are also possibly confusing, as there are both positive and negative levels.

{% highlight python %}
fulldatadf[['Condition1','Condition2']].value_counts()
Condition1  Condition2
Norm        Norm          2522
Feedr       Norm           155
Artery      Norm            89
RRAn        Norm            41
PosN        Norm            35
RRAe        Norm            28
PosA        Norm            17
RRAn        Feedr            8
RRNn        Norm             7
RRNe        Norm             6
Feedr       Feedr            4
PosN        PosN             4
PosA        PosA             3
Feedr       RRNn             2
Artery      Artery           2
Feedr       RRAn             1
RRAn        Artery           1
Feedr       RRAe             1
            Artery           1
Artery      PosA             1
RRNn        Artery           1
            Feedr            1
{% endhighlight %}

Based on the numbers here, I will create 4 new binary features:

<table border="1" class="dataframe">
  <thead>
	<tr style="text-align: right">
   	  <th class="text">New column name</th>
	  <th class="text">Old levels</th>
	  <th class="text">Description</th>
	</tr>
  </thead>
  <tbody>
	<tr>
 	  <td data-title="New column name" class="text">RRAdj</td>
	  <td data-title="Old levels" class="text">RRAn, RRAe</td>
	  <td data-title="Description" class="text">Adjacent to any railroad (N-S or E-W)</td>
	</tr>
	<tr>
 	  <td data-title="New column name" class="text">RRNear</td>
	  <td data-title="Old levels" class="text">RRNn, RRNe</td>
	  <td data-title="Description" class="text">Near any railroad (N-S or E-W), excluding adjacent</td>
	</tr>
	<tr>
 	  <td data-title="New column name" class="text">RoadAdj</td>
	  <td data-title="Old levels" class="text">Artery, Feedr</td>
	  <td data-title="Description" class="text">Adjacent to arterial or feeder street</td>
	</tr>
	<tr>
 	  <td data-title="New column name" class="text">PosNear</td>
	  <td data-title="Old levels" class="text">PosN, PosA</td>
	  <td data-title="Description" class="text">Adjacent to or near positive off-site feature</td>
	</tr>
  </tbody>
</table>

I believe this creation of simple features, although losing a degree of granularity, will cut down on computation and improve performance, especially if our pipeline involves one hot encoding categorical features.

#### HouseStyle ####
This feature has 8 levels, where there are 2 levels for 1.5 story homes (finished and unfinished), 2 levels for 2.5 story homes (finished and unfinished) and 2 levels for split homes. I will merge the finished and unfinished for each style as their IQRs and means are not too far off, and there are relatively few instances of each.

<p align=center>
<img src="/assets/images/HouseStylePreMergeSalePriceBoxPlot.svg" alt="Boxplot showing relation between Sale Price and HouseStyle" width = '90%'>
<br><sub>Before merge</sub><br>
<img src="/assets/images/HouseStylePostMergeSalePriceBoxPlot.svg" alt="Boxplot showing relation between Sale Price and HouseStyle" width = '90%'>
<br><sub>After merge</sub>
</p>

#### RoofStyle  ####

I will merge `Flat` with `Shed` to decrease underpopulated levels. (Additionally, I\'m of the mind that a flat roof is a type of a shed roof, as according to one of the definitions I found, it can have up to a 10 degree slope in one direction and still be considered flat.)

{% highlight python %}
# after merge
fulldatadf['RoofStyle'].value_counts()
Gable      2318
Hip         547
Shed         25
Gambrel      22
Mansard      11
{% endhighlight %}

#### RoofMatl ####
A lot of these have single samples - we\'re going to group everything besides `CompShg` and `Tar&Grv` under a generic `Other`.

{% highlight python %}
# after merge
fulldatadf['RoofMatl'].value_counts()
CompShg    2881
Other        42
{% endhighlight %}

#### Exterior1st + Exterior2nd ####
First, there are some typos in `Exterior2nd`: `CmentBd` is used instead of `CemntBd`, and `Wd Shng` is used instead of `WdShing`. After cleaning these up, only 66 samples do not have the same values for `Exterior1st` and `Exterior2nd`, over half with only 1 sample per combination. To decrease the number of combinations left, I will merge `Stone`, `CBlock`, `ImStucc`, `PreCast`  and `AsphShn` into `Other`, and `BrkComm` with `BrkFace` to make `Brick`.

One other issue is of alphabetical ordering - `Exterior1st` and `Exterior2nd` do not imply ordering, they are just 2 different exterior materials used on the house. So I rearranged the pairs so that `[Plywood, Brick]` has the same arrangement as `[Brick, Plywood]`.

{% highlight python %}
# post merge, last 10 groups
fulldatadf.groupby('Exterior1st')['Exterior2nd'].value_counts()[-10:]
Exterior1st  Exterior2nd
Stucco       Stucco           32
             Wd Sdng           5
             WdShing           5
             VinylSd           1
VinylSd      VinylSd        1006
             WdShing           9
             Wd Sdng           5
Wd Sdng      Wd Sdng         358
             WdShing          20
WdShing      WdShing          41
{% endhighlight %}

#### MasVnrType ####
As done earlier, I combined `BrkComm` with `BrkFace` to make `Brick`, and merge the single `CBlock` into `Stone`.
{% highlight python %}
# post merge
fulldatadf['MasVnrType'].value_counts()
None     1773
Brick     904
Stone     246
{% endhighlight %}

#### Foundation ####
Combine `Stone` and `Wood` into `Other` due to low cardinality.
{% highlight python %}
# post merge
fulldatadf['Foundation'].value_counts()
PConc     1307
CBlock    1240
BrkTil     311
Slab        49
Other       16
{% endhighlight %}

#### Heating ####
Combine all levels except for `GasA` and `GasW`.
{% highlight python %}
# post merge
fulldatadf['Heating'].value_counts()
GasA     2879
GasW       26
Other      18
{% endhighlight %}

#### CentralAir ####
This feature will go from a 'Y' / 'N' column to a binary 1 / 0 column.

{% highlight python %}
# post mapping
fulldatadf['CentralAir'].value_counts()
1    2727
0     196
{% endhighlight %}

#### MiscFeature ####
I will not be merging anything here, despite low cardinality, due to the large differences in `MiscVal` when grouped by levels, as seen below:
{% highlight python %}
fulldatadf.groupby('MiscFeature')['MiscVal'].mean()
MiscFeature
Gar2    8760.00
TenC    2000.00
Othr    3250.00
Shed     767.32
None       0.00
{% endhighlight %}

#### SaleType ####
Similar to `HouseStyle`, I will merge these based on their similar categories:

<table border="1" class="dataframe">
  <thead>
	<tr style="text-align: right">
   	  <th class="text">Old SaleType level</th>
	  <th class="text">Description</th>
	  <th class="text">New SaleType level</th>
	</tr>
  </thead>
  <tbody>
	<tr>
 	  <td data-title="Old SaleType level" class="text">WD</td>
	  <td data-title="Description" class="text">Warranty Deed - Conventional</td>
	  <td data-title="New SaleType level" class="text">WD</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">CWD</td>
	  <td data-title="Description" class="text">Warranty Deed - Cash</td>
	  <td data-title="New SaleType level" class="text">WD</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">VWD</td>
	  <td data-title="Description" class="text">Warranty Deed - VA loan</td>
	  <td data-title="New SaleType level" class="text">WD</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">New</td>
	  <td data-title="Description" class="text">Home just constructed and sold</td>
	  <td data-title="New SaleType level" class="text">New</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">COD</td>
	  <td data-title="Description" class="text">Court Officer Deed / Estate</td>
	  <td data-title="New SaleType level" class="text">Other</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">Con</td>
	  <td data-title="Description" class="text">Contract 15% Down payment regular terms</td>
	  <td data-title="New SaleType level" class="text">Con</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">ConLw</td>
	  <td data-title="Description" class="text">Contract Low Down payment and low interest</td>
	  <td data-title="New SaleType level" class="text">Con</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">ConLI</td>
	  <td data-title="Description" class="text">Contract Low Interest</td>
	  <td data-title="New SaleType level" class="text">Con</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">ConLD</td>
	  <td data-title="Description" class="text">Contract Low Down</td>
	  <td data-title="New SaleType level" class="text">Con</td>
	</tr>
	<tr>
 	  <td data-title="Old SaleType level" class="text">Oth</td>
	  <td data-title="Description" class="text">Other</td>
	  <td data-title="New SaleType level" class="text">Other</td>
	</tr>
  </tbody>
</table>

<p align=center>
<img src="/assets/images/SaleTypePreMergeSalePriceBoxPlot.svg" alt="Boxplot showing relation between Sale Price and HouseStyle" width = '90%'>
<br><sub>Before merge</sub><br>
<img src="/assets/images/SaleTypePostMergeSalePriceBoxPlot.svg" alt="Boxplot showing relation between Sale Price and HouseStyle" width = '90%'>
<br><sub>After merge</sub>
</p>

#### Sale Condition ####
First, we can look at the distribution of `SalePrice` when sorted by `SaleCondition`:

<p align=center>
<img src="/assets/images/SaleConditionSalePriceBoxPlot.svg" width = '90%'>
</p>

What we do now depends entirely on what kinds of homes we want to predict the `SalePrice` of. If the goal is to predict an average home for a potential home buyer, the model should look only at `Normal` sales, since other types are not representative of prices seen. If the goal is to predict the price of any real estate transaction in Ames, Iowa, all data points should be kept.

In this case, even though `Abnorml`, `Family`, `Alloca`, and `AdjLand` make up 9.2% of our dataset, I will not keep these samples in the dataset. Because my goal is to predict the price of a home for a potential home buyer, the model should only see prices associated with typical sales.

{% highlight python %}
# filter 'SaleCondition' by including
# Normal and Partial sales only
salecondition_cols = ['Normal', 'Partial']

salecondition_mask = fulldatadf['SaleCondition'].isin(salecondition_cols)

fulldatadf = fulldatadf[salecondition_mask]
{% endhighlight %}

___

### Final comments ###

A reminder that all graphing and cleaning code can be found <a href="">on my github</a>, and a quick recap of what the data looks like after cleaning and filtering:

{% highlight python %}
fulldatadf.shape
(2635, 83)
{% endhighlight %}

<table border="1" class="dataframe">
  <thead>
	<tr style="text-align: right">
   	  <th class="text">Action</th>
	  <th class="text">Columns</th>
	</tr>
  </thead>
  <tbody>
	<tr>
 	  <td data-title="Action" class="text">Dropped</td>
	  <td data-title="Columns" class="text">Order, MSSubClass, Condition1, Condition2</td>
	</tr>
	<tr>
 	  <td data-title="Action" class="text">Added</td>
	  <td data-title="Columns" class="text">RRAdj, RRNear, RoadAdj, PosNear, isPUD</td>
	</tr>
  </tbody>
</table>

___

### What\'s up next ###

* In one of my next posts, I want to talk about building a python module with all of my cleaning functions inside, so my `working.py` script remains readable, and functions are easily repeatable for my next data cleaning project

* In another post, I will talk about the process of scraping web results in order to obtain address data to use with an API that uses GPS coordinates to calculate the distance between a home and specific features within Ames, Iowa

* Finally, I want make a post about building the model, and testing it against unseen data obtained from the Ames site.

If you see anything in my posts that you want to comment on, [send me an email](mailto:contact@aimee.codes) and let me know the issue!

Until next time!