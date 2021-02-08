## Chargement du package 
# Deux methodes possibles pour générer des scénarios aléatoires : 
# Method 1 : "Interface fonctions" Générer manuellement et invididuellement le scenario de chaque type d'actif
# Method 2 : "Interface objet" Creer un objet "scenario" du package esg qui va generer automatiquement un scénario pour tous les types d'actifs.
library(ESG)

# Donnees input : Courbe des prix zero-coupons //Je ne sais pas vraiment ce que c'est comme données : pas de doc dessus
data(ZC)
plot(ZC)

#######################################################################################
# Method 1 : "Interface fonctions" Générer manuellement et invididuellement le scenario de chaque type d'actif
########################################################################################

## 1 - Actions et taux court

simulStock <- rStock(horizon=40, nScenarios=1000, ZC=ZC, vol=.1, k=2, volStock=.2, stock0=100, rho=.5)

## 2 - Taux courts, immo, d?faut, liquidit?

rt <- rShortRate(horizon=40, nScenarios=1000, ZC=ZC, vol=.1, k=2)
re <- rRealEstate(horizon=40, nScenarios=1000, ZC=ZC, vol=.1, k=2, volRealEstate=.15, realEstate0=50)
ds <- rDefaultSpread(horizon=40, nScenarios=1000, defaultSpread0=.01, volDefault=.2, alpha=.1, beta=1)
ls <- rLiquiditySpread(horizon=40, nScenarios=1000, eta=.05, liquiditySpread0=.01)
par(mfrow=c(3,2))
matplot(t(simulStock$stockPaths), type='l', xlab = "horizon", ylab = "action")
matplot(t(rt), type='l', xlab = "horizon", ylab = "taux court")
matplot(t(re$realEstatePaths), type='l',  xlab = "horizon", ylab = "immobilier")
matplot(t(ds), type='l', xlab = "horizon", ylab = "spread de d?faut")
matplot(t(ls), type='l', xlab ="horizon", ylab = "spread de liquidit?")

# Ecriture des fichiers csv
write.table(x = rt, file = "gse_outputs/esg_shortrate.csv", sep = ",", row.names = FALSE, col.names = FALSE)
write.table(x = simulStock$stockPaths, file = "gse_outputs/esg_stock.csv", sep = ",", row.names = FALSE, col.names = FALSE)
write.table(x = re$realEstatePaths, file = "gse_outputs/esg_realestate.csv", sep = ",", row.names = FALSE, col.names = FALSE)
write.table(x = ds, file = "gse_outputs/esg_defaultspread.csv", sep = ",", row.names = FALSE, col.names = FALSE)
write.table(x = ls, file = "gse_outputs/esg_liquidityspread.csv", sep = ",", row.names = FALSE, col.names = FALSE)

## 3 - Tous les facteurs de risque, sur un m?me horizon en une seule fois avec la fonction rAllRisksFactors

simulAllRiskFactors <- rAllRisksFactors(horizon=40, nScenarios=1000, ZC, vol=.1, k=2, volStock=.2, stock0=100, rho=.5, volRealEstate=.15, realEstate0=50, eta=.05, liquiditySpread0=.01, defaultSpread0=.01, volDefault=.2, alpha=.1, beta=1)
par(mfrow=c(2,2))
matplot(t(simulAllRiskFactors$shortRate), type='l', xlab = "horizon", ylab = "taux court")
matplot(t(simulAllRiskFactors$s), type='l', xlab = "horizon", ylab = "stocks")
matplot(t(simulAllRiskFactors$realEstate), type='l', xlab = "horizon", ylab = "immobilier")
matplot(t(simulAllRiskFactors$defaultSpread), type='l', xlab = "horizon", ylab = "spread de d?faut")

#############################################################################################
# Method 2 : "Interface objet" Creer un objet "scenario" du package esg qui va generer automatiquement 
# un scénario pour tous les types d'actifs. (mais je ne sais pas comment cela s'utilise)
#############################################################################################

scenarios1 <- new("Scenarios")
scenarios1 <- setParamsBaseScenarios(scenarios1, horizon=40, nScenarios=10000)
scenarios1 <- scenarios1 <- setRiskParamsScenarios(scenarios1, vol=.1, k=2,volStock=.2,
                                                   volRealEstate=.15, volDefault=.2, alpha=.1,beta=1, eta=.05,rho=.5, stock0=100,realEstate0=50,
                                                   liquiditySpread0=.01, defaultSpread0=.01)

data(ZC)
scenarios1 <- setZCRates(scenarios1, ZC, horizon=40)
#getZCRates(scenarios1)
#getrealEstatePaths(scenarios1)