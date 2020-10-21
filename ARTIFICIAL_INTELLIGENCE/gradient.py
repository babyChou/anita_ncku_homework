import numpy as np


def gradientDescent(x, y, theta, alpha, m, numIterations):
    xTrans = x.transpose()
    for i in range(0, numIterations):
        hypothesis = np.dot(x, theta)
        loss = hypothesis - y

        cost = np.sum(loss ** 2) / (2 * m)
        print("Iteration %d | Cost: %f" % (i, cost))

        gradient = np.dot(xTrans, loss) / m

        theta = theta - alpha * gradient
    return theta


data = np.array([
    [ 5, 45, 77],
    [ 5.11, 26, 47],
    [ 5.6, 30, 55],
    [ 5.9, 34, 59],
    [ 4.8, 40, 72],
    [ 5.8, 36, 60],
    [ 5.3, 19, 40],
    [ 5.8, 28, 60],
    [ 5.5, 23, 45],
    [ 5.6, 32, 58]
])

guessX = np.array([ 5.5, 38])

rowX, colX = np.indices((10, 2))
rowY = np.array(range(10))
colY = np.array([2]*10)

x = data[rowX, colX]
y = data[rowY, colY]

m, n = np.shape(x)
numIterations= 100
alpha = 0.0005

theta = np.ones(n)
theta = gradientDescent(x, y, theta, alpha, m, numIterations)
h = theta.dot(guessX)

print('theta:', theta)
print('answer:', h)

# theta: [1.19318799 1.6127044 ]
# answer: 67.84530124035801