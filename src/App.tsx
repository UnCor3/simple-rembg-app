import JSZip from "jszip";
import { FormEvent, useState } from "react";

const App = () => {
  const [status, setStatus] = useState("idle");
  const [imgs, setImgs] = useState<string[]>([]);
  const handleOnSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const formData = new FormData(e.currentTarget);
      const res = await fetch("http://localhost:3001/rembg", {
        method: "POST",
        body: formData,
      });
      !res.ok && setStatus("error");
      const blob = await res.blob();
      const files = await unzipBlob(blob);
      setImgs(files);
    } catch (error) {
      console.log(error);
      setStatus("error");
    }
  };

  if (status === "error") return <div>Error...</div>;

  return (
    <div className="container">
      <h1>Remove background</h1>
      <p>Choose some image to start</p>
      <form onSubmit={handleOnSubmit}>
        {/*key is required to reset the input field */}
        <input type="file" multiple name="images" key={Date.now()} />
        <button type="submit" disabled={status !== "idle"}>
          Remove background
        </button>
      </form>
      {imgs.length ? (
        <>
          Here are your image(s)
          <div className="img-container">
            {imgs.map((img, i) => (
              <img src={img} alt="" key={i} />
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
};

async function unzipBlob(blob: Blob) {
  const zipIns = new JSZip();
  const files: string[] = [];
  return await zipIns.loadAsync(blob).then(async (ctt) => {
    const promises: Promise<void>[] = [];

    //can be done better
    //but readability decreases
    ctt.forEach((_, file) => {
      const promise = file.async("blob").then((data) => {
        files.push(URL.createObjectURL(data));
      });
      promises.push(promise);
    });

    await Promise.all(promises);
    return files;
  });
}

export default App;
