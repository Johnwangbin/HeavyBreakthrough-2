display selected stocks infos

getFromDB

closePriceCurve     InAnHour
turnOverCurve
currentMACD
lastFiveDaysChangeRatio

save selected stocks infos

find and collect stocks meeting the conditions:

closePriceCurve in special features ...

turnover normalization
calculate MACD value
getModelsFromNewDatas In two and one class


examineModelsInVastDatas    In two and one class


4-6
am: using linear kernel achieves good result.
    one class model have more strict conditions but two class.
    add one point to the curve, alter the scale of the Y axis.
pm: training a new model with only curves.training set is selected by hand,
    test set is randomly generated.
    Watching the curve of the test vector to judge the correction of the result.
    packaging the flow of a model's generation and testing.

    to do:packaging the displaying of curve obtained by the time in various files.
          validating the model via datas in databases.

4-7
am: training:when training set is modified, it must be trained again.
    training one set have two output models.
    testing: when test set is modified, it must be tested again.
    one test set should be tested with two models.
pm: consider where the name of dir should be added, what level of package should be added.
    implement the traverse of all stocks's data.
    study the means of normalization used in the libsvm.

    to do: implementation of work flow of two class classfication