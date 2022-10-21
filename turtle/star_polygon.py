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

        Draw a regular star polygon (https://en.wikipedia.org/wiki/Star_polygon)
        defined by the radius of the circumscribing circle and by its Schlafli
        symbol {n/m} where n is the number of vertices and m is the step used
        to connect the vertices. The vertices are numbered from 0 to n-1 and
        regularly placed on the circle. Starting from the vertex 0, the star is
        built step by step by connecting the vertex i to the vertex (i+m) % n
        until the initial vertex 0 is reached. If n and m are coprime (d=gcd(n,m)=1),
        all vertex are reached and the star is done.
        if n and m are not coprime (d>1) the construction is done via
        stellation: the figure is composed of d star polygons {(n//d) / (m//d)}
        e.g.: hexagram {6/2} is composed of 2 triangles: {6/2} ==> 2x{3}
              {12/3} ==> 3x{4}       {30/12} ==> 6x{5/2}

        See: https://en.wikipedia.org/wiki/Star_polygon
         and https://en.wikipedia.org/wiki/Stellation 

        The step m is expected to be between 1 and n-1. m=1 corresponds to a
        regular convex polygon noted {n} (which can be also be traced with 
        circle(radius, steps=n)). Values between n/2 and n-1 invert the direction
        of the drawing.
        if m<0 the star polygon {n/-m} is drawn sequentially. Each star point
        is connected to the next one by 2 edges (forming a \/). The result is
        a star figure without interior segments (only the external hull is
        drawn, i.e. without any crossing lines).
        
        Alternatively, it is possible to omit the step m and to provide edgelen:
        the length of star edges (those forming the \/). 
        
        If neither step nor edgelen is provided, m is computed as (n-1)//2
        
        This method shares several similarities with circle(radius): 
            - It begins and ends drawing the figure at the same position,
            - A regular convex polygon can be similarly drawn either with
              circle(radius, steps=n) or with star(radius, n, 1) and
            - If circle(radius, steps=n) is used to draw a polygon {n}, the
              vertices also corresponds to the vertices of any star {n/m}.
            - It draws the star in counterclockwise direction if radius is
              positive, otherwise in clockwise direction. NB: a m>n//2 also
              inverts the direction.
              
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

        # Use short variable names (see figure StarPolygonData.png)
        
        r = radius
        n = vertices
        m = step
        u = edgelen

        pi = math.pi
        pi2 = pi * 2.0

        onlyHull = True
        if m is None and u is None:
            m = max(1, (n-1) // 2)
        if m is not None:
            u = None
            if m >= 0:
                onlyHull = False
            else:
                m = -m
                if m <= 0 or m >= n:
                    raise TurtleGraphicsError("Bad argument for step should be in [1..%d]" % (n - 1))
                if m > n / 2:  # result in the inversion of the drawing
                    m = n - m
                    r = -r     # report the inversion to r to handle stellation in the chosen direction 
        
        sgn = 1
        if r < 0:
            sgn = -1
        
        if not onlyHull: # mode {m/n} with internal edges (as done by hand for a 5-points star)
            alpha = sgn * pi2 / n
            beta = alpha * (m + 1.0) / 2.0  # 1->0.5 2->1.5, 3->2, 4->2.5, ...
            gamma = alpha * m
            delta = sgn * (n - 2.0) / n * pi
            s = 2.0 * r * math.sin(alpha / 2.0)
            t = 2.0 * r * math.sin(gamma / 2.0)
        elif u is None: # mode {m/n} without internal edges, compute u (edgelen) from r, n and m
            alpha = sgn * pi2 / n
            gamma = alpha * m
            delta = sgn * (n - 2.0) / n * pi
            theta = pi - gamma
            rho = (delta - theta) / 2.0
            lambd = pi - (alpha + theta) / 2.0
            sigma = pi - 2.0 * rho
            u = math.sin(alpha / 2.0) * r / math.sin(lambd)
        else: # mode n and u (thus without internal edges)
            r = sgn * r
            alpha = sgn * pi2 / n
            delta = sgn * (n - 2.0) / n * pi
            s = 2.0 * r * math.sin(alpha / 2.0)
            if u < s / 2.0:
                raise TurtleGraphicsError("Bad argument for edgelen should be greater than %.2f" % (s / 2.0))
            rho = math.acos(s / (2.0 * u))
            theta = delta - 2.0 * rho
            sigma = pi - 2.0 * rho

        # save state
        
        orient = self.heading()
        posit = self.position()
        full = self._fullcircle
        self.radians() # from now use angles expressed in radians

        if not onlyHull: # mode {m/n} with internal edges (as done by hand for a 5-points star)
            
            d = math.gcd(n, m)
            n1 = n // d

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
                for i in range(d - 1):
                    self.forward(s)
                    self._rotate(-alpha)
                self.pendown()
                
        else: # no internal edges, only the external shape (hull) with edgelen = u
            
            self._rotate((pi - theta) / 2.0)
            for i in range(n):
                self.forward(u)
                self._rotate(sigma - pi)
                self.forward(u)
                self._rotate(pi - theta)

        # restore state
        
        self.degrees(full)

        self.penup()
        self.goto(posit)
        self.pendown()

        self.setheading(orient)

        if self.undobuffer:
            self.undobuffer.cumulate = False

# A little demo                

if __name__ == "__main__":
    # start of glue code (for integration in module turtle.py do not copy this glue code)
    t0 = TurtleEx() 
    def getturtle():
        return t0
    def exitonclick():
        t0.getscreen().exitonclick()
    # end of glue code
    
    # this demos can be copied (or not) in the turtle.py module
    def demo3():
        """Demo of the star() new feature."""
        r=250
        n=7   # test with different n (5, 8, 12...)

        turtle = getturtle()
        turtle.reset()
        turtle.clear()
        turtle.hideturtle()

        turtle.dot()

        turtle.penup()
        turtle.sety(-r)
        turtle.pendown()

        turtle.speed('fastest')
        turtle.circle(r)
        turtle.color('green')

        # trace a convex regular polygon. Could be done with turtle.star(r, n, 1) but use
        # circle() to check vertices share the same location with both methods
        # turtle.circle(r, steps = n)

        turtle.color('black', 'yellow')
        turtle.begin_fill()
        turtle.star(r, n, 2)
        turtle.color('blue')
        turtle.star(r, n, -3)
        turtle.color('orange')
        turtle.star(r, n, edgelen=220)
        turtle.star(r, n, edgelen=200)
        turtle.color('lightblue')
        turtle.end_fill()

        time.sleep(1)
        while turtle.undobufferentries():
            turtle.undo()

    def demo4():
        """Demo to recreate the turtle star figure of https://docs.python.org/3.3/library/turtle.html."""
        turtle = getturtle()
        turtle.reset()
        turtle.hideturtle()
        turtle.speed('fastest')
        turtle.clear()
        turtle.color('red', 'yellow')
        turtle.begin_fill()
        turtle.star(100, 36)
        turtle.end_fill()
        turtle.up()
        turtle.right(150)
        turtle.forward(80)
        turtle.color('green')
        turtle.write("  Click to exit", font = ("Arial", 14, "bold") )

    # these invocations can be copied in the turtle.py module
    # demo2() should be well termlinated if demo3() and/or demo4() is executed after
    demo3()
    demo4()
    exitonclick()
