import numpy as np

class ppb():
    """
    Classe permet de moséliser la Provision pour Participation au Bénéfice
    """
    def __init__(self, ppb_historique_initiale) -> None:
        """
        Constructeur.

        :params ppb_historique_initiale: provision pour participation au bénéfice initiale.
        """
        self.ppb_historique = ppb_historique_initiale
        self.dotations = np.array([])
        self.reprises = np.array([])
        self.consommation = 0
        # TODO  codeer la consomation de PPB à tout instant depuis le début de l'année
        # TODO corriger les dotations reprises

    def reprise_ppb_8ans(self):
        """
        Méthode permettant de reprendre la provision pour participation au bénéfice stockée 8 ans auparavant.
        """
        if len(self.ppb_historique) >= 8:
            ppb_8ans =  self.ppb_historique[-8]
            self.ppb_historique[-8]  = 0
            self.consommation = self.consommation + ppb_8ans
            #return ppb_8ans
        #else:
            #return 0

    def reprise_ppb(self, montant_a_reprendre):
        """
        Méthode permettant de reprendre/soustraire un certain montant à la PPB.

        :params montant_a_reprendre: (Float) Montant à reprendre.
        """
        reste = min(montant_a_reprendre, np.sum(self.ppb_historique))
        self.reprises = np.append(self.reprises, montant_a_reprendre)
        self.consommation = self.consommation + montant_a_reprendre
        for i in range(len(self.ppb_historique),0,-1):
            if self.ppb_historique[i-1] < reste :
                reste = reste - self.ppb_historique[i-1]
                self.ppb_historique[i-1] = 0
            else:
                self.ppb_historique[i-1] = self.ppb_historique[i-1] - reste
                reste = 0
                break

    def dotation_ppb(self, montant_a_doter):
        """
        Méthode permettant de Doter/Ajouter un certain montant à la PPB.

        :params montant_a_doter: (Float) Montant à doter.
        """
        #self.ppb_historique = np.append(self.ppb_historique, montant_a_doter)
        self.dotations = np.append(self.dotations, montant_a_doter)
        self.consommation = self.consommation - montant_a_doter
    
    def re_init_ppb(self):
        """
        Methode permettant de reinitialiser la provision pour participation au bénéfice en fin de période pour la période suivante.
        """
        self.ppb_historique = np.append(self.ppb_historique, np.sum(self.dotations))
        self.reprises = np.array([])
        self.dotations = np.array([])
        self.consommation = 0