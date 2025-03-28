CONTAINER_NAME = web

ps: ## Смотреть список запущенных контнейнеров всего, в текущем проекте и именв
	docker ps && docker-compose ps && docker-compose ps --services

build: ## Собрать images Docker
	docker-compose build

start: ## Запустить контейнеры Docker
	docker-compose up --build -d

stop_bot: ## Остановить контейнер bot для отладки
	docker-compose stop bot && python run_polling.py 

bash: ## Открыть оболочку bash в контейнере web, для создания суперпользователя 
	docker-compose exec $(CONTAINER_NAME) bash -c 'python manage.py createsuperuser'

logs_celery: ## смотреть протоколы в контейнере celery 
	docker-compose logs -f celery

drop: ## Остановить и удалить контейнеры Docker
	docker-compose down -v

rm_and_clean_containers:  ## Остановить, удалить и очистить все контейнеры
	docker stop $$(docker ps -a -q) &&  docker rm $$(docker ps -a -q) && docker system prune -f

rm_and_clean_images:  ## Удалить и очистить все образы
	docker rmi $$(docker images -a -q) && docker system prune -f

push:
	@read -p "Введите комментарий: " COMMENT; \
	git add * && \
	git commit -am "$$COMMENT" && \
	git push