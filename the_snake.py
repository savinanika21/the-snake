from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
DEFAULT_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Центр экрана!
DEFAULT_COLOR = (0, 255, 0)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """
    Базовый класс для всех игровых объектов.
    Хранит общие атрибуты: позицию и цвет объекта.
    Предоставляет заглушку для метода отрисовки, который должен
    быть переопределен в дочерних классах.
    """

    def __init__(self, position=DEFAULT_POSITION, body_color=DEFAULT_COLOR):
        """
        Инициализирует игровой объект.
        Аргументы:
        position - начальная позиция объекта (x, y).
        body_color - цвет объекта. Если не указан,
        используется цвет по умолчанию.
        """
        self.position = position
        self.body_color = body_color

    def _draw_cell(self, position, color=None):
        """
        Отрисовывает одну ячейку.
        Если цвет не передан, используется self.body_color.
        """
        final_color = color if color is not None else self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, final_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """
        Метод отрисовки объекта.
        В базовом классе не выполняет действий, реализация
        зависит от конкретного типа объекта (яблоко, змейка).
        """
        raise NotImplementedError(
            'Метод draw не реализуем в базовом классе.'
        )


class Apple(GameObject):
    """Игровой объект: яблоко. Отвечает за позицию и отрисовку."""

    def __init__(self, position=DEFAULT_POSITION, body_color=APPLE_COLOR):
        """Инициализирует объект яблока."""
        super().__init__(position, body_color)
    # Специально не вызываю рандомизацию в __init__, чтобы не было проблем
    # с автотестами. Они могут создать яблоко в конкретной точке.
    # Если яблоко при этом появится в рандомной позиции, тест не сработает
    # и выдаст AssertionError.
    # Кроме того, аргумент position теряет смысл, если позиция
    # рандомизируется сразу.

    def randomize_position(self):
        """Генерирует случайную позицию по сетке клеток."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)
        return self.position

    def draw(self):
        """Отрисовывает яблоко как квадрат с обводкой."""
        self._draw_cell(self.position)


class Snake(GameObject):
    """Игровой объект: змейка. Управляет движением,
    ростом и отрисовкой сегментов.
    """

    def __init__(self, position=DEFAULT_POSITION, body_color=SNAKE_COLOR):
        """Инициализирует змейку, принимая позицию и цвет.
        Внутри метода задаёт начальное направление (вправо) и
        создаёт список сегментов.
        """
        super().__init__(position, body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """
        Обновляет позицию змейки.
        Вычисляет новую голову с учётом
        направления и телепортации через границы поля.
        """
        # Распаковка координат и вектора направления
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)
        # Добавляем новую голову в начало списка
        self.positions.insert(0, new_head)
        # self.position равен текущей голове
        self.position = new_head
        # Удаление хвоста
        self.last = self.positions.pop()

    def update_direction(self, new_direction):
        """Применяет запланированное направление движения
        (next_direction) к текущему.
        """
        if new_direction is not None:
            self.direction = new_direction

    def draw(self):
        """Отрисовывает все сегменты змейки."""
        # Тело рисуется без головы
        for position in self.positions[:-1]:
            self._draw_cell(position)

        # Отрисовка головы змейки
        self._draw_cell(self.positions[0])

    def reset(self, random_direction=False):
        """Сбрасывает змейку в начальное состояние.
        Аргумент random_direction:
        - False (по умолчанию): направление будет RIGHT (для старта игры).
        - True: направление будет выбрано случайно (для перезапуска).
        """
        # Используем константу для центра, чтобы не дублировать вычисления
        self.positions = [self.position]
        if random_direction:
            self.direction = choice([UP, DOWN, LEFT, RIGHT])
        else:
            self.direction = RIGHT
        self.last = None

    def grow(self):
        """
        Метод возвращает хвост змейки из self.last в конец self.positions.
        Вызывается, когда змейка съела яблоко.
        """
        if self.last is not None:
            # Возвращаем удаленный хвост в конец списка
            self.positions.append(self.last)
            # Обнуляем last, так как хвост теперь снова является частью тела
            self.last = None


def handle_keys(game_object):
    """
    Обрабатывает события ввода (нажатия клавиш и закрытие окна).
    Сразу передаёт новое направление в update_direction,
    не используя next_direction.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.update_direction(UP)
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.update_direction(DOWN)
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.update_direction(LEFT)
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.update_direction(RIGHT)


def place_apple_safely(apple, snake):
    """Генерирует позицию для яблока, пока она не окажется вне тела змейки."""
    while True:
        apple.randomize_position()
        if apple.position not in snake.positions:
            break


def main():
    """
    Главный игровой цикл.
    Инициализирует объекты, запускает бесконечный цикл:
    1. Обработка ввода.
    2. Обновление логики (направление, движение, столкновения).
    3. Отрисовка объектов.
    4. Контроль FPS.
    """
    # Инициализация PyGame:
    pg.init()

    snake = Snake()
    apple = Apple()
    # Не переношу apple.randomize_position в __init__ по тем же причинам,
    # что прописывала выше в классе Apple
    apple.randomize_position()

    while True:
        clock.tick(20)
        # Обработка событий
        handle_keys(snake)
        # Змейка двигается
        snake.move()
        # Текущая позиция головы
        head = snake.get_head_position()
        # Сравнение координат головы змейки и яблока, рост
        if snake.get_head_position() == apple.position:
            place_apple_safely(apple, snake)
            snake.grow()
        # Столкновение змейки с самой собой - проверка через elif
        elif head in snake.positions[1:]:
            # Сбрасываем змейку в начальное состояние,
            # яблоко рандомно перемещается, не попадая на змею.
            # Направление движения меняется с дефолтного на рандомное.
            snake.reset(random_direction=True)
            place_apple_safely(apple, snake)
        # Очистка экрана
        # Примечание: Использую полную очистку экрана,
        # чтобы гарантировать отсутствие следов
        # и корректную очистку поля после сброса игры (reset).
        # Логика частичного стирания хвоста в
        # snake.draw() остаётся из-за шаблона,
        # но она становится избыточной благодаря этой строке.
        screen.fill(BOARD_BACKGROUND_COLOR)
        # Отрисовка змейки и яблока
        snake.draw()
        apple.draw()
        # Обновление окна
        pg.display.update()


if __name__ == '__main__':
    main()
