import os
import grpc

import video_service_pb2 as pb2
import video_service_pb2_grpc as pb2_grpc

CHUNK_SIZE = 64 * 1024  # 64KB


def generate_upload_chunks(filepath, title):
    filename = os.path.basename(filepath)

    # 1) Enviar metadata
    metadata = pb2.VideoMetadata(
        filename=filename,
        title=title
    )
    yield pb2.UploadChunk(metadata=metadata)

    # 2) Enviar datos del archivo en chunks
    with open(filepath, "rb") as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            yield pb2.UploadChunk(data=data)


def main():
    local_video_path = "C:/Users/sauld/Videos/Captures/2025-10-22-22-40-15.mp4"
    video_title = "No se"

    if not os.path.exists(local_video_path):
        print(f"[CLIENT] No se encontró el archivo local: {local_video_path}")
        return

    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.VideoServiceStub(channel)

    print(f"[CLIENT] Subiendo video: {local_video_path}")
    response = stub.UploadVideo(
        generate_upload_chunks(local_video_path, video_title)
    )

    print(f"[CLIENT] Upload success: {response.success}")
    print(f"[CLIENT] Message: {response.message}")
    print(f"[CLIENT] Nombre guardado en servidor: {response.stored_filename}")


if __name__ == "__main__":
    main()
