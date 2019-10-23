from turtle import Turtle, TurtleGraphicsError
import math
import time


class TurtleEx(Turtle, TurtleGraphicsError):

    def star(self, radius, vertices, step=None, edgelen=None):
        """
        Draw a regular star polygon
        
        Arguments:
        radius -- a number
        vertices -- a positive integer
        step (optional) - an integer
        edgelen (optional) -- a positive number

        Draw a 2D regular star (https://en.wikipedia.org/wiki/Star_polygon):
        a regular non-convex polygon, noted {n/m} where n is the number of
        vertices and m is the step used to connect the vertices. radius is
        the radius of the (virtual) enclosing circle on which the star points
        (vertices) are regularly placed. The star is built by connecting the
        vertex i to the vertex i+step along the circle. step is expected to
        be between 1 (resulting in a regular convex polygon) and n/2. 
        
        if n and m are not coprime (k=gcd(n,m)>1) the construction is done via
        stellation: the figure is composed of k star polygons {(n/k) / (m/k)}
        e.g.: hexagramme {6/2} is composed of 2 triangles: {6/2} ==> 2x{3}
              {12/3} ==> 3x{4}       {30/12} ==> 6x{5/2}

        if m<0 the star polygon {n/-m} is drawn sequentially. Each star point
        is connected to the next one by 2 edges (forming a \/). The result is
        a star figure without interior segments (only the external hull is
        drawn, i.e. without any crossing lines).
        
        Alternatively, it is possible to provide edgelen: the length of star
        edges (those forming the \/). In that case, no value should be
        provided for the step m.
        
        If neither step nor edgelen is provided, m is computed as (n-1)//2
        
        This method shares several similarities with circle(radius): 
            - it begins and ends drawing the figure at the same position,
            - if circle(radius, steps=n) is used to draw a polygon {n}, the
              vertices also corresponds to the vertices of any star {n/m}.
            - it draws the star in counterclockwise direction if radius is
              positive, otherwise in clockwise direction.
              
        At the end, the position and orientation are the same as at the start
        (even in case of stellation).
        
        Examples (for a Turtle instance named turtle):
        >>> turtle.circle(150, steps=5)
        >>> turtle.star(150, 5)
        
        >>> turtle.star(150, 7, edgelen=120)
        
        >>> turtle.color('red', 'yellow')
        >>> turtle.begin_fill()
        >>> turtle.star(100, 36)
        >>> turtle.end_fill()
        """

        if self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = True

        # Use short variable names
        
        r = radius
        n = vertices
        m = step
        u = edgelen

        onlyHull = True
        if m is None and u is None:
            m = max(1, (n-1) // 2)
        if m is not None:
            u = None
            if m >= 0:
                onlyHull = False
            else:
                m = -m
            if m > n / 2:
                m = n - m
        
        sgn = 1
        if r < 0:
            sgn = -1
        
        if not onlyHull: # mode {m/n} with internal edges (as done by hand for a 5-points star)
            alpha = sgn * 360.0 / n
            beta = alpha * (m + 1.0) / 2.0  # 1->0.5 2->1.5, 3->2, 4->2.5, ...
            gamma = alpha * m
            delta = sgn * (n - 2.0) / n * 180.0
            s = 2.0 * r * math.sin(alpha / 2.0 * math.pi / 180.0)
            t = 2.0 * r * math.sin(gamma / 2.0 * math.pi / 180.0)
        elif u is None: # mode {m/n} without internal edges, compute u (edgelen) from r, n and m
            alpha = sgn * 360.0 / n
            gamma = alpha * m
            delta = sgn * (n - 2.0) / n * 180.0
            theta = 180.0 - gamma
            rho = (delta - theta) / 2.0
            lambd = 180.0 - (alpha + theta) / 2.0
            sigma = 180.0 - 2.0 * rho
            u = math.sin(alpha / 2.0 * math.pi / 180.0) * r / math.sin(lambd * math.pi / 180.0)
        else: # mode n and u (thus without internal edges)
            r = sgn * r
            alpha = sgn * 360.0 / n
            delta = sgn * (n - 2.0) / n * 180.0
            s = 2.0 * r * math.sin(alpha / 2.0 * math.pi / 180.0)
            if u < s / 2.0:
                raise TurtleGraphicsError("Bad argument for edgelen should be greater than %.2f" % (s / 2.0))
            rho = math.acos(s / (2 * u)) / math.pi * 180.0
            theta = delta - 2.0 * rho
            sigma = 180.0 - 2.0 * rho

        # save state
        
        orient = self.heading()
        posit = self.position()
        full = self._fullcircle
        self.degrees() # from now use angles expressed in classical 360 degrees

        if not onlyHull: # mode {m/n} with internal edges (as done by hand for a 5-points star)
            
            k = math.gcd(n, m)
            n1 = n // k

            self._rotate(-gamma/2)
            for i in range(n):
                if i and i % n1 == 0: # go forward to next vertex for stellation
                    self._rotate(beta)
                    self.penup()
                    self.forward(s)
                    self.pendown()
                    self._rotate(beta)
                else:
                    self._rotate(gamma)
                self.forward(t)

            if self.filling():  # go backward to ensure filling will be ok (finish at start point)
                self.penup()
                self._rotate(beta + delta)    
                for i in range(k - 1):
                    self.forward(s)
                    self._rotate(-alpha)
                self.pendown()
                
        else: # no internal edges, only the external shape (hull) with edgelen = u
            
            self._rotate(90 - theta / 2)
            for i in range(n):
                self.forward(u)
                self._rotate(sigma - 180)
                self.forward(u)
                self._rotate(180 - theta)

        # restore state
        
        self.degrees(full)

        self.penup()
        self.goto(posit)
        self.pendown()

        self.setheading(orient)

        if self.undobuffer:
            self.undobuffer.cumulate = False

# A little demo                

t = TurtleEx()

r=250
n=7

t.hideturtle()
t.dot()

t.penup()
t.sety(-r)
t.pendown()

t.speed('fastest')
t.circle(r)
t.color('green')
t.star(r, n, 1) # a convex regular polygon (can also be done with t.circle(r, steps = n))

t.color('black', 'yellow')
t.begin_fill()
t.star(r, n, 2)
t.color('blue')
t.star(r, n, -3)
t.color('orange')
t.star(r, n, edgelen=220)
t.star(r, n, edgelen=200)
t.color('lightblue')
t.end_fill()

time.sleep(1)
while t.undobufferentries():
    t.undo()
        
t.reset()
t.hideturtle()
t.speed('fastest')
t.clear()
t.color('red', 'yellow')
t.begin_fill()
t.star(100, 36)
t.end_fill()


