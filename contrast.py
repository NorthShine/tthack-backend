import cv2


def edit_contrast(frame, alpha):
    adjusted = cv2.convertScaleAbs(frame, alpha=alpha)

    # for tests only
    # cv2.imshow('adjusted', adjusted)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    return adjusted


if __name__ == "__main__":
    frame = cv2.imread("1.jpg")
    edit_contrast(frame, 5)
