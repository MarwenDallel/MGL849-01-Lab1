import multiprocessing
import queue


class SharedPriorityQueue:
    def __init__(self):
        """
        Initialise une nouvelle instance de la file d'attente à priorité partagée.

        En Python, la bibliothèque multiprocessing ne fournit pas de file d'attente à
        priorité native (PriorityQueue) qui soit sûre pour les processus. Par conséquent,
        cette classe a été implémentée pour fournir une structure de données similaire qui
        peut être utilisée de manière sécurisée à travers différents processus.

        Cette file utilise la Queue de multiprocessing pour partager des éléments entre
        processus et un Lock pour synchroniser l'accès à ces éléments.
        """
        self.queue = multiprocessing.Queue()  # La file d'attente entre les processus
        self.lock = (
            multiprocessing.Lock()
        )  # Le verrou pour contrôler l'accès concurrent

    def put(self, item, priority):
        """
        Ajoute un élément avec une priorité spécifiée à la file d'attente.

        Args:
            item: L'élément à ajouter à la file.
            priority: La priorité de l'élément, les éléments avec une priorité plus faible
                      seront traités en premier.
        """
        with self.lock:  # Acquisition du verrou pour garantir l'accès exclusif à la file
            wrapped_item = (priority, item)  # Envelopper l'élément avec sa priorité
            self.queue.put(wrapped_item)  # Ajouter l'élément enveloppé à la file

    def get(self):
        """
        Récupère et retourne l'élément avec la plus haute priorité (la plus basse valeur numérique)
        de la file d'attente.

        Les éléments sont d'abord retirés, triés par priorité, puis remis dans la file,
        ce qui est nécessaire puisque nous n'avons pas de PriorityQueue native qui gérerait
        cela automatiquement.

        Returns:
            L'élément avec la plus haute priorité ou None si la file est vide.
        """
        with self.lock:  # Acquisition du verrou pour garantir l'accès exclusif à la file
            try:
                # Extraire tous les éléments pour pouvoir les trier par priorité
                items = []
                while not self.queue.empty():
                    items.append(self.queue.get_nowait())

                # Trier les éléments par leur priorité (la valeur la plus basse en premier)
                items.sort(key=lambda x: x[0])

                # Remettre tous les éléments dans la file sauf celui avec la plus haute priorité
                for item in items[1:]:
                    self.queue.put(item)

                # Retourner l'élément avec la plus haute priorité s'il y en a un
                return items[0][1] if items else None
            except queue.Empty:
                # Si la file est vide, retourner None
                return None

    def empty(self):
        """
        Vérifie si la file d'attente est vide.

        Returns:
            Un booléen indiquant si la file est vide (True) ou non (False).
        """
        with self.lock:  # Acquisition du verrou pour garantir l'accès exclusif à la file
            return self.queue.empty()  # Retourne si la file est vide ou non
