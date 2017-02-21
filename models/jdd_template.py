class Student:
    def __init__(self):
        location_lower = location.lower()
        if location_lower == "cc":
            self.location = "Centre de Châtillon"
        elif location_lower == "cm":
            self.location = "Centre de Meudon"
        elif location_lower == "cp":
            self.location = "Centre de Palaiseau"
        elif location_lower == "cl":
            self.location = "Centre de Lilles"
        elif location_lower == "ct":
            self.location = "Centre de Toulouse"
        else:
            self.location = location
    def __unicode__(self):
        return "{name} ({department}/{unit}, {grade})".format(
                name=self.name,
                grade=self.grade,
                department=self.department,
                unit=self.unit
                )

    def __str__(self):
        return unicode(self)

class PhD:

    def __unicode__(self):
        return self.title

    def __str__(self):
        return unicode(self)

class Supervizor:
    def __init__(self):
        title_lower = title.lower()
        if not title_lower:
            self.title = ""
        elif title_lower == "docteur":
            self.title = "Dr."
        elif title_lower == "docteur, avec hdr":
            self.title = "Dr. HDR"
        elif title_lower == "professeur":
            self.title = "Pr."
        elif title_lower == "maître de conférence":
            self.title = "MDC"
        elif title_lower == "ingénieur":
            self.title = "Ing."
        elif title_lower == "ingénieur de recherche":
            self.title = "Ing."
        elif title_lower == "directeur de recherche":
            self.title = "DR"
        elif title_lower == "chargé de recherche":
            self.title = "CR"
        else:
            self.title = title
    def __unicode__(self):
        output = self.title + '~' if self.title else ""
        output += self.name
        output += ' (' + self.department + '/' + self.unit + ')' \
                if self.unit else ' (' + self.department + ')' \
                if self.department else ' (' + self.origin + ')' \
                if self.origin else ''
        return output

    def __str__(self):
        return unicode(self)

class Director:
    def __unicode__(self):
        if not self.department:
            output = self.title + '~' if self.title else ""
            output += "{name} ({origin})".format(
                    name=self.name,
                    origin=self.origin
                    )
            return output
        else:
            return super(Director, self).__unicode__()