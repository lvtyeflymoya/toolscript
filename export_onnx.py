from ultralytics import YOLO

if __name__ == '__main__':
    # Load a model
    model = YOLO("C:/Users/Zhang/Desktop/best_2.pt")

    # Export the model
    model.export(format="onnx",
                 opset=11, 
                 simplify=True,
                 imgsz=1024,
                 dynamic=False,
                 half=True)