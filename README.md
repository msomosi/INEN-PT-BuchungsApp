# INEN-PT-BuchungsApp
 Die "Buchungs- und Reservierungsplattform für ein Studentenwohnheim" stellt eine innovative Lösung im Bereich der digitalen Buchungssysteme dar, die sich nahtlos in den Alltag einer Fachhochschule integriert.

How to start local:
cd buchungsmanagement
docker build -t booking:latest .
docker run -d -p 5002:5002 booking:latest

cd..
cd login-service
docker build -t login:latest .
docker run -d -p 5001:5001 login:latest

cd..
cd zimmerverwaltung
docker build -t room:latest .
docker run -d -p 5003:5003 room:latest