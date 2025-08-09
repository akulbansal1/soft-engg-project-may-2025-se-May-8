import React, { useEffect, useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Trash2,
  PlusCircle,
  ArrowLeft,
  UploadCloud,
  FileText,
  Download,
  AlertTriangle,
  Pencil,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const BASE_URL = "/api/v1"; // Use the proxy

interface Document {
  id: number;
  name: string;
  file_url: string;
  timestamp: string;
}

const DataVaultPage: React.FC = () => {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [modalOpen, setModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [docToDelete, setDocToDelete] = useState<Document | null>(null);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingName, setEditingName] = useState("");

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentName, setDocumentName] = useState("");
  const [error, setError] = useState("");

  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // READ: Fetch documents when the component mounts
  useEffect(() => {
    if (user) {
      setIsLoading(true);
      fetch(`${BASE_URL}/documents/user/${user.id}`)
        .then((res) => {
          if (!res.ok) throw new Error("Failed to fetch documents");
          return res.json();
        })
        .then((data: Document[]) => setDocuments(data))
        .catch((err) => {
          console.error("Fetch documents error:", err);
          toast.error("Could not load your documents.");
        })
        .finally(() => setIsLoading(false));
    }
  }, [user]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setDocumentName(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!user || !selectedFile || !documentName) {
      setError("Please select a file and provide a name.");
      return;
    }

    setUploading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const uploadRes = await fetch(`${BASE_URL}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const errDetail = await uploadRes.json();
        throw new Error(errDetail.detail || "File upload failed");
      }

      const uploadResult = await uploadRes.json();
      const { file_url } = uploadResult;

      const createPayload = {
        user_id: user.id,
        name: documentName,
        file_url: file_url,
      };

      const createRes = await fetch(`${BASE_URL}/documents/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createPayload),
      });

      if (!createRes.ok) {
        const errDetail = await createRes.json();
        throw new Error(errDetail.detail || "Failed to create document record");
      }

      const newDocument = await createRes.json();
      setDocuments((prev) => [newDocument, ...prev]);
      setModalOpen(false);
      setSelectedFile(null);
      setDocumentName("");
      toast.success("Document uploaded successfully!");
    } catch (err: any) {
      console.error("Upload process error:", err);
      setError(err.message || "An unexpected error occurred.");
      toast.error("Upload failed", { description: err.message });
    } finally {
      setUploading(false);
    }
  };

  const handleRename = async (docId: number) => {
    const originalDoc = documents.find((d) => d.id === docId);
    if (!editingName || !originalDoc || editingName === originalDoc.name) {
      setEditingId(null);
      return;
    }

    try {
      const res = await fetch(`${BASE_URL}/documents/${docId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: editingName }),
      });

      if (!res.ok) {
        const errDetail = await res.json();
        throw new Error(errDetail.detail || "Failed to rename document");
      }

      const updatedDoc = await res.json();
      setDocuments((prev) =>
        prev.map((d) => (d.id === docId ? updatedDoc : d))
      );
      toast.info(`Renamed to "${updatedDoc.name}"`);
    } catch (err: any) {
      toast.error("Rename failed", { description: err.message });
      // Revert the name in UI if API call fails
      setDocuments((prev) => [...prev]);
    } finally {
      setEditingId(null);
    }
  };

  const startEditing = (doc: Document) => {
    setEditingId(doc.id);
    setEditingName(doc.name);
  };

  const openDeleteConfirm = (doc: Document) => {
    setDocToDelete(doc);
    setConfirmDeleteOpen(true);
  };

  const handleDelete = async () => {
    if (!user || !docToDelete) return;
    try {
      const res = await fetch(`${BASE_URL}/documents/${docToDelete.id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errDetail = await res.json();
        throw new Error(errDetail.detail || "Failed to delete document");
      }
      setDocuments((prev) => prev.filter((doc) => doc.id !== docToDelete.id));
      toast.success(`"${docToDelete.name}" was deleted.`);
      setConfirmDeleteOpen(false);
      setDocToDelete(null);
    } catch (err: any) {
      console.error("Delete error:", err);
      toast.error("Deletion failed", { description: err.message });
    }
  };

  const SkeletonLoader = () => (
    <div className="space-y-4 pt-4">
      {[...Array(3)].map((_, i) => (
        <Card key={i} className="p-4 animate-pulse">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 bg-muted rounded-md"></div>
              <div>
                <div className="h-6 w-40 bg-muted rounded mb-2"></div>
                <div className="h-4 w-24 bg-muted rounded"></div>
              </div>
            </div>
            <div className="flex space-x-2">
              <div className="h-8 w-8 bg-muted rounded-md"></div>
              <div className="h-8 w-8 bg-muted rounded-md"></div>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="h-[calc(100dvh-110px)] flex flex-col space-y-6 overflow-hidden">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold flex items-center">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/home")}
            className="mr-4"
          >
            <ArrowLeft size={20} />
          </Button>
          Data Vault
        </h2>
        <Button variant="outline" size="sm" onClick={() => setModalOpen(true)}>
          <PlusCircle className="mr-2" size={16} /> Upload Document
        </Button>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden bg-transparent">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Your Documents
            {!isLoading && (
              <Badge variant="secondary">{documents.length}</Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-hidden">
          <ScrollArea className="h-full pr-4">
            {isLoading ? (
              <SkeletonLoader />
            ) : documents.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>No documents found. Upload one to get started.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {documents.map((doc) => (
                  <Card key={doc.id} className="p-4">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-4">
                        <FileText className="w-8 h-8 text-primary" />
                        <div>
                          {editingId === doc.id ? (
                            <Input
                              value={editingName}
                              onChange={(e) => setEditingName(e.target.value)}
                              onBlur={() => handleRename(doc.id)}
                              onKeyDown={(e) => {
                                if (e.key === "Enter") handleRename(doc.id);
                                if (e.key === "Escape") setEditingId(null);
                              }}
                              autoFocus
                              className="text-lg"
                            />
                          ) : (
                            <p className="font-semibold text-lg">{doc.name}</p>
                          )}
                          <p className="text-sm text-muted-foreground">
                            Uploaded on:{" "}
                            {new Date(doc.timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <a
                          href={doc.file_url}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label="Download document"
                          >
                            <Download size={16} />
                          </Button>
                        </a>
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label="Rename document"
                          onClick={() => startEditing(doc)}
                        >
                          <Pencil size={16} />
                        </Button>
                        <Button
                          variant="destructive"
                          size="icon"
                          aria-label="Delete document"
                          onClick={() => openDeleteConfirm(doc)}
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Upload Dialog */}
      <Dialog open={modalOpen} onOpenChange={setModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload a New Document</DialogTitle>
            <DialogDescription>
              Select a file from your device and give it a name.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadCloud className="mr-2 h-4 w-4" />
              {selectedFile ? "Change File" : "Select File"}
            </Button>
            <Input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              className="hidden"
            />
            {selectedFile && (
              <p className="text-sm text-muted-foreground">
                Selected: {selectedFile.name}
              </p>
            )}

            <Input
              placeholder="Document Name (e.g., Blood Report)"
              value={documentName}
              onChange={(e) => setDocumentName(e.target.value)}
              disabled={!selectedFile}
            />
            {error && (
              <p className="text-sm text-red-500 text-center">{error}</p>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploading || !selectedFile || !documentName}
            >
              {uploading ? "Uploading..." : "Upload and Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={confirmDeleteOpen} onOpenChange={setConfirmDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="text-destructive" /> Are you sure?
            </DialogTitle>
            <DialogDescription>
              This action cannot be undone. This will permanently delete the
              document
              <span className="font-semibold text-foreground">
                {" "}
                "{docToDelete?.name}"
              </span>
              .
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setConfirmDeleteOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Yes, delete document
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DataVaultPage;
